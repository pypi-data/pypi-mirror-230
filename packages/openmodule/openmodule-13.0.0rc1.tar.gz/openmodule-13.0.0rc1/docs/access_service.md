# Access Service

Inherit from either

* Access Service: No session handling and no access sync
* AccessServiceWithSessions: Session handling (check in, check out, errors) and no access sync
* AccessServiceWithDatabase: With Access Sync and no session handling
* AccessServiceWithDatabase and AccessServiceWithSessions: Session handling and access sync

The Access Service module also provides some functions, that are commonly used by the Access Service implementations

* `get_lpr_id_search`: Is used to convert the given license plate to our license plate search structure.
* `deduplicate_accesses`: Can be used to make sure, that no duplicates are in the return value of the `AccessCheckResponse`
* `find_lpr_accesses`: Returns the correct accesses for the license plates, that matched via our Matching Config
* `check_accesses_valid_at_time`: This function marks accesses invalid if they expired or are not yet valid
* `check_accesses_valid_at_gate`: Marks accesses invalid if e.g. the accesses does not have the current gate in their
  parksetting

For a more detailed guide set the [Access Service Documentation](https://youtrack.acc.si/articles/DEV-A-1187/).

## Access Service

You have to implement the `rpc_check_access` function and probably add some other custom stuff.

An example implementations is shown below.

```python
def rpc_check_access(self, request: AccessCheckRequest, _) -> AccessCheckResponse:
    """
    Check if the user has access at the given gate at the given time according to DEV-A-916
    """
    self.log.debug(f"Check Access for {request.vehicle} at gate {request.gate}")

    accesses = []
    if request.vehicle.lpr:
        accesses += self.find_lpr_accesses(request.vehicle.lpr)
        accesses += self.find_regex_accesses(request.vehicle.lpr)
    if request.vehicle.qr:
        accesses += self.find_qr_accesses(request.vehicle.qr)

    accesses = deduplicate_accesses(accesses)

    # we mark the access invalid, if the access is currently not valid or the gate is incorrect for the access
    check_accesses_valid_at_time(accesses, request.timestamp)
    if request.gate:
        check_accesses_valid_at_gate(accesses, request.gate, self.settings)

    self.log.info(f"Found {len(accesses)} matching accesses "
                  f"where {len([a for a in accesses if a.accepted])} are valid")
    return AccessCheckResponse(success=True, accesses=accesses)
```

## AccessServiceWithSessions

In addition to the Access Service stuff implement the session handling functions `check_in_session`, `check_out_session`
and `check_out_session`

## AccessService and KVStore

A running version of the Python snippets can be found in the [Test Cases](../tests/test_utils_access_service.py) file.

A Access Service often has some kind of database where the parking permissions are saved. For saving a parking  
permission into a local database the KVStore can be used.

First you have to create your own database model that inherits from `KVEntry`.

```python
class TestAccessModelBase(Base, KVEntry):
    __test__ = False
    __tablename__ = "test_access_model"

    # the KVEntry uses the field `key` as primary key, but we prefer our normal primary key 'id'
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, value):
        self.key = value

    # ids for open session service
    customer_id = Column(String, nullable=True)  # id used by open session service (customer id)
    car_id = Column(String, nullable=True)  # id used by open session service (customer car id)
    group_id = Column(String, nullable=True)  # id by open session service (contract id)

    parksettings_id = Column(String, nullable=True)  # None is allowed for simplicity as only gates are necessary

    access_infos = Column(JSONEncodedDict, nullable=True)  # infos attached to all messages, null is empty dict

    # lpr with matching config
    lpr_id = Column(String, nullable=True)
    lpr_id_search = Column(String, nullable=True, index=True)
    lpr_country = Column(String, nullable=True)
    matching_scheme = Column(String, nullable=True)
    matching_version = Column(Integer, nullable=True)

    # other media
    qr_id = Column(String, nullable=True, index=True)
    regex = Column(String, nullable=True, index=True)

    @classmethod
    def parse_value(cls, value) -> dict:
        """Parses the value from the server into a dict of {column-name: value}"""
        return value


# this is just a convenience method that patches lpr_id_search,
# so that I don't need to set the lpr_id_search explicit on model creation
@event.listens_for(TestAccessModelBase, "before_update", propagate=True)
@event.listens_for(TestAccessModelBase, "before_insert", propagate=True)
def before_insert_and_update(_, __, target: TestAccessModelBase):
    if target.lpr_id:
        target.lpr_id_search = get_lpr_id_search(target.lpr_id)

    if (target.lpr_id is None) != (target.lpr_country is None):
        raise ValueError("field `lpr_country` must also be set iff `lpr_id` is set.")

    if not any([target.lpr_id, target.qr_id, target.regex]):
        raise ValueError("No id or regex set in access")
```

You have to manually implement the `parse_value` method, that parses the value from the server into kwargs for the
KVEntry constructor. In this method you have to manually convert the field values to the correct database types.
For example, you have to convert the `datetime` string to a `datetime` object.

```python
@classmethod
def parse_value(cls, value) -> dict:
    # we have to manually parse the start and end date times
    value["start"] = datetime.datetime.fromisoformat(value["start"]) if "start" in value else None
    value["end"] = datetime.datetime.fromisoformat(value["end"]) if "end" in value else None
    return value
```

After our local database is defined. We can create our KVStore, that will handle the KV sync for us.
More information about the KVStore can be found [here](database.md#key-value-store).

```python
class TestAccessKVStore(KVStore):
    database_table = TestAccessModelBase
```

The KVStore provides a hook method `parse()`, that can be used to generate more local database models, from the
KV data. In the section [Mutliple KVStore](access_service.md#multiple-kvstore) you can find an example, how to use this
hook.

At last, we have to implement the `rpc_check_access` method.

## Multiple KVStore

A running version of the Python snippets can be found in the [Test Cases](../tests/test_utils_kv_store_multiple.py)
file.

If you have more data sources for a single access service, you have to use the `MultipleKVStores` class.
The MultipleKVStores class is a wrapper around multiple KVStores. It provides the same some `run()`, `register_rpcs()`
and `shutdown()` functions as the KVStore.
Every KVStore in the MutlipleKVStores has to have the parameter `suffix` set. This suffix is used as an
identifier for the KV sync channel.

First we define our local database structure as we would normally do.

```python
class CarData(pydantic.BaseModel):
    license_plate: str
    country: str
    customer_car_id: Optional[str]
    matching_scheme: Optional[str]
    matching_version: Optional[int]


class Contract(Base, KVEntry):
    __tablename__ = "contracts"

    # because the primary key of the KV entry is named 'key' we provide getter and setter for our preferred name 'id'
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, value):
        self.key = value

    contract_id = Column(String, nullable=False)  # group id for controller
    group_limit = Column(Integer, nullable=True)
    access_infos = Column(JSONEncodedDict, nullable=True)
    barcode = Column(String, nullable=True)  # qrcode

    # 1 to many relationship to our license plate table
    # relationship to child tables with cascade delete that deletes orphaned entries as well
    # this relationship is needed for correct deletion of the additional tables
    cars: List['Car'] = relationship("Car", back_populates="contract", cascade="all, delete", passive_deletes=True)

    def __init__(self, *args, cars_data: Optional[List[CarData]] = None, **kwargs):
        self.cars_data: Optional[List[CarData]] = cars_data
        super().__init__(*args, **kwargs)

    @classmethod
    def parse_value(cls, value) -> dict:
        # this method has to be implemented by the child class, and therefore we validate cars json payload here
        # with Pydantic model parse_obj_as() function
        cars_data = value.pop("cars", None)
        if cars_data is not None:
            # validate car json payload with Pydantic model
            value["cars_data"] = pydantic.parse_obj_as(List[CarData], cars_data)
        return value


class Reservation(Base, KVEntry):
    __tablename__ = "reservations"

    # because the primary key of the KV entry is named 'key' we provide getter and setter for our preferred name 'id'
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, value):
        self.key = value

    # a reservation has a start and an end date
    start = Column(TZDateTime, nullable=False)
    end = Column(TZDateTime, nullable=False)
    barcode = Column(String, nullable=False)  # qrcode

    # 1 to 1 relationship to our car table
    car: 'Car' = relationship("Car", back_populates="reservation", cascade="all, delete", passive_deletes=True,
                              uselist=False)

    def __init__(self, *args, car_data: Optional[CarData] = None, **kwargs):
        self.car_data: Optional[CarData] = car_data  # car data has to be present on sync (set)
        super().__init__(*args, **kwargs)

    @classmethod
    def parse_value(cls, value) -> dict:
        # this method has to be implemented by the child class, and therefore we validate car json payload here
        # with Pydantic model parse_obj() method
        value["car_data"] = CarData.parse_obj(value.pop("car", None))
        # we have to manually parse the start and end date times
        value["start"] = datetime.datetime.fromisoformat(value["start"]) if "start" in value else None
        value["end"] = datetime.datetime.fromisoformat(value["end"]) if "end" in value else None
        return value


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lpr_id = Column(String, nullable=False)
    lpr_search_id = Column(String, nullable=False, index=True)
    lpr_country = Column(String, nullable=False)
    customer_car_id = Column(String, nullable=True)
    matching_scheme = Column(String, nullable=True)
    matching_version = Column(Integer, nullable=True)

    # foreign keys to parent table - BEWARE contracts.id is just a wrapper in python!
    contract_id = Column(String, ForeignKey("contracts.key", ondelete="CASCADE"), nullable=True)
    contract = relationship("Contract", back_populates="cars")
    reservation_id = Column(String, ForeignKey("reservations.key", ondelete="CASCADE"), nullable=True)
    reservation = relationship("Reservation", back_populates="car")
```

In the above example we define a 1 to many relations ship for `Contract` and `Car`
and a 1 to 1 relationship for `Reservation` and `Car`.
To implement this relationship we have to add a foreign key to the child table and a relationship to the parent table.

In the `parse_value` method we have to manually parse the incoming data from the server into our database model.
In this method we use the [Pydantic](https://docs.pydantic.dev/latest/) model to verify the incoming nested data.

We now have to use the KVStore hook method `parse()` to create the child tables from the KV data.

```python
class KVStoreContracts(KVStore):
    database_table = Contract

    def parse(self, contracts: List[Contract]) -> List[Car]:
        """We create additional models for our local database"""
        instances = []
        for contract in contracts:
            assert contract.barcode or contract.cars_data, "Either a barcode or cars must be present"
            if contract.cars_data:
                c: CarData
                for c in contract.cars_data:
                    # you have to manually set the lpr_search_id with the clean function
                    car = Car(contract=contract, lpr_id=c.license_plate,
                              lpr_search_id=access_utils.get_lpr_id_search(c.license_plate),
                              lpr_country=c.country, customer_car_id=c.customer_car_id,
                              matching_scheme=c.matching_scheme, matching_version=c.matching_version)
                    instances.append(car)
        return instances


class KVStoreReservations(KVStore):
    database_table = Reservation

    def parse(self, reservations: List[Reservation]) -> List[Car]:
        """We create additional models for our local database"""
        instances = []
        for r in reservations:
            # you have to manually set the lpr_search_id with the clean function
            car = Car(reservation=r, lpr_id=r.car_data.license_plate,
                      lpr_search_id=access_utils.get_lpr_id_search(r.car_data.license_plate),
                      lpr_country=r.car_data.country, customer_car_id=r.car_data.customer_car_id,
                      matching_scheme=r.car_data.matching_scheme, matching_version=r.car_data.matching_version)
            instances.append(car)
        return instances
```

With the hook method `parse()` we can represent the local database structure as we want.

Now we almost finished. We have to create our `MultipleKVStores` instance and register our KVStores.

```python
kv_store_contracts = KVStoreContracts(self.database, self.core.rpc_client, suffix="contracts")
kv_store_reservations = KVStoreReservations(self.database, self.core.rpc_client, suffix="reservations")
multi_store = MultipleKVStores(self.kv_store_contracts, self.kv_store_reservations)
multi_store.register_rpcs(self.rpc_server)
multi_store.run()
```

Now you can implement your Access Service with your chosen local database structure.
