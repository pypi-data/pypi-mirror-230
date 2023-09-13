import datetime
import time
from textwrap import dedent
from typing import List, Optional
from unittest.mock import patch

import pydantic
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import openmodule.utils.access_service as access_utils
from openmodule.config import override_settings
from openmodule.database.custom_types import JSONEncodedDict, TZDateTime
from openmodule.models.kv_store import KVSetRequest, KVSetRequestKV, KVSyncRequest, KVSetResponse, KVSyncResponse
from openmodule.rpc import RPCServer
from openmodule.utils.kv_store import KVStore, KVEntry, MultipleKVStores
from openmodule_test.core import OpenModuleCoreTestMixin
from openmodule_test.database import SQLiteTestMixin
from openmodule_test.rpc import RPCServerTestMixin

Base = declarative_base()


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


@override_settings(NAME="om_access_test_1")
class MultipleKVStoresTestCase(SQLiteTestMixin, RPCServerTestMixin, OpenModuleCoreTestMixin):
    alembic_path = "../tests/test_kv_store_multiple_database"
    database_name = "kvstore_mutliple"
    rpc_channels = ["kv_sync", "rpc-websocket"]

    def setUp(self):
        super().setUp()
        self.rpc_server = RPCServer(self.zmq_context())
        self.rpc_server.run_as_thread()

    def setup_multi_kv_store(self):
        self.kv_store_contracts = KVStoreContracts(self.database, self.core.rpc_client, suffix="contracts")
        self.kv_store_reservations = KVStoreReservations(self.database, self.core.rpc_client, suffix="reservations")
        self.assertEqual(self.kv_store_contracts.service_name, "om_access_test_contracts")
        self.assertEqual(self.kv_store_reservations.service_name, "om_access_test_reservations")
        # the multiple kv store class is used to register the RPCs,
        # because you cannot have more handlers for the same channel and type
        self.multi_store = MultipleKVStores(self.kv_store_contracts, self.kv_store_reservations)
        self.multi_store.register_rpcs(self.rpc_server)
        self.wait_for_rpc_server(self.rpc_server)

    def tearDown(self):
        self.rpc_server.shutdown()
        super().tearDown()

    def test_random_offset_for_kv_stores(self):
        # we have to patch the testing() method so that the method returns something
        with patch("openmodule.utils.kv_store.testing") as mock:
            mock.return_value = False
            offset_contracts = KVStoreContracts(suffix="om_access_arivo2_contracts")
            offset_reservations = KVStoreReservations(suffix="om_access_arivo2_reservations")
            self.assertNotEqual(offset_contracts, offset_reservations)

    def test_kv_store_raises_an_assertion_error_if_suffix_is_set_and_register_rpcs_is_called(self):
        kv_store_without_suffix = KVStoreContracts(self.database, self.core.rpc_client)
        kv_store_without_suffix.register_rpcs(self.rpc_server)
        kv_store_with_suffix = KVStoreReservations(self.database, self.core.rpc_client, suffix="suffix")
        self.assertRaises(AssertionError, kv_store_with_suffix.register_rpcs, self.rpc_server)

    def test_kv_store_create_and_delete(self):
        self.setup_multi_kv_store()

        set_request = KVSetRequest(service=self.kv_store_contracts.service_name, kvs=[
            KVSetRequestKV(key="test1", e_tag=1, previous_e_tag=None,
                           value=dedent("""
                           {
                            "contract_id": "0000-FEED-0000-0001",
                            "group_limit": 1,
                            "access_infos": {
                                "test": "test"
                            },
                            "cars": [
                                {
                                    "customer_car_id": "car1",
                                    "license_plate": "G:TEST1",
                                    "country": "A",
                                    "matching_scheme": "DEFAULT",
                                    "matching_version": 20
                                },
                                {
                                    "customer_car_id": "car2",
                                    "license_plate": "LÖ:TEST2",
                                    "country": "D",
                                    "matching_scheme": "DEFAULT",
                                    "matching_version": 10
                                }
                            ]
                           }
                           """)),
            KVSetRequestKV(key="test2", e_tag=2, previous_e_tag=None,
                           value=dedent("""
                           {
                            "contract_id": "Fancy Contract Id",
                            "barcode": "DEADBEEF"
                           }
                           """)),
            KVSetRequestKV(key="test3", e_tag=3, previous_e_tag=None,
                           value=dedent("""
                           {
                            "contract_id": "`o##o>",
                            "barcode": "1CE1CE1CE",
                            "cars": [
                                {
                                    "customer_car_id": "car3",
                                    "license_plate": "ASDF1",
                                    "country": "-"
                                },
                                {
                                    "customer_car_id": "car4",
                                    "license_plate": "SEMMEL1",
                                    "country": "A"
                                },
                                {
                                    "customer_car_id": "car5",
                                    "license_plate": "AMSOFA1",
                                    "country": "A"
                                }
                            ]
                           }
                           """)),
        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            # check contract data
            contract = db.query(Contract).filter(Contract.id == "test1").first()
            self.assertIsNotNone(contract)
            self.assertEqual("0000-FEED-0000-0001", contract.contract_id)
            self.assertEqual(1, contract.group_limit)
            self.assertDictEqual({"test": "test"}, contract.access_infos)
            self.assertEqual(2, len(contract.cars))
            contract = db.query(Contract).filter(Contract.id == "test2").first()
            self.assertIsNotNone(contract)
            self.assertEqual("Fancy Contract Id", contract.contract_id)
            self.assertEqual("DEADBEEF", contract.barcode)
            self.assertIsNone(contract.group_limit)
            self.assertIsNone(contract.access_infos)
            self.assertEqual([], contract.cars)
            contract = db.query(Contract).filter(Contract.id == "test3").first()
            self.assertIsNotNone(contract)
            self.assertEqual("`o##o>", contract.contract_id)
            self.assertIsNone(contract.group_limit)
            self.assertIsNone(contract.access_infos)
            self.assertEqual(3, len(contract.cars))
            # check car data
            car = db.query(Car).filter(Car.lpr_search_id == "GTEST1").first()
            self.assertIsNotNone(car)
            self.assertEqual("car1", car.customer_car_id)
            self.assertEqual("G:TEST1", car.lpr_id)
            self.assertEqual("A", car.lpr_country)
            self.assertEqual("DEFAULT", car.matching_scheme)
            self.assertEqual(20, car.matching_version)
            car = db.query(Car).filter(Car.lpr_search_id == access_utils.get_lpr_id_search("LÖTEST2")).first()
            self.assertIsNotNone(car)
            self.assertEqual("car2", car.customer_car_id)
            self.assertEqual("LÖ:TEST2", car.lpr_id)
            self.assertEqual("D", car.lpr_country)
            self.assertEqual("DEFAULT", car.matching_scheme)
            self.assertEqual(10, car.matching_version)
            car = db.query(Car).filter(Car.lpr_search_id == "ASDF1").first()
            self.assertIsNotNone(car)
            self.assertEqual("car3", car.customer_car_id)
            self.assertEqual("ASDF1", car.lpr_id)
            self.assertEqual("-", car.lpr_country)
            self.assertIsNone(car.matching_scheme)
            self.assertIsNone(car.matching_version)

        # delete all entries
        set_request = KVSetRequest(service=self.kv_store_contracts.service_name, kvs=[
            KVSetRequestKV(key="test1", e_tag=None, previous_e_tag=1, value='null'),
            KVSetRequestKV(key="test2", e_tag=None, previous_e_tag=2, value='null'),
            KVSetRequestKV(key="test3", e_tag=None, previous_e_tag=3, value='null'),
        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            self.assertEqual(0, db.query(Contract).count())
            self.assertEqual(0, db.query(Car).count())
            self.assertEqual(0, db.query(Reservation).count())

        # create reservation entries
        set_request = KVSetRequest(service=self.kv_store_reservations.service_name, kvs=[
            KVSetRequestKV(key="test4", e_tag=4, previous_e_tag=None,
                           value=dedent("""
                                       {
                                        "start": "2023-09-05T17:57:12",
                                        "end": "2023-09-05T19:00:00",
                                        "barcode": "C0FFEE",
                                        "car": {
                                            "license_plate": "RESERVATION1",
                                            "country": "-"
                                        }
                                       }
                                       """)),
            KVSetRequestKV(key="test5", e_tag=5, previous_e_tag=None,
                           value=dedent("""
                                   {
                                     "start": "2000-01-01T12:12:12",
                                     "end": "2001-01-01T01:01:01",
                                     "barcode": "BARCODE",
                                     "car": {
                                          "license_plate": "RESERVATION2",
                                          "country": "-"
                                     }
                                   }
                                   """)),

        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            # check reservation data
            reservation = db.query(Reservation).filter(Reservation.id == "test4").first()
            self.assertIsNotNone(reservation)
            self.assertIsNotNone(reservation.start)
            self.assertTrue(isinstance(reservation.start, datetime.datetime))
            self.assertIsNotNone(reservation.end)
            self.assertTrue(isinstance(reservation.end, datetime.datetime))
            self.assertEqual("C0FFEE", reservation.barcode)
            self.assertEqual(reservation.car.lpr_id, "RESERVATION1")
            self.assertEqual(reservation.car.lpr_search_id, access_utils.get_lpr_id_search("RESERVATION1"))
            self.assertEqual(reservation.car.lpr_country, "-")
            self.assertIsNone(reservation.car.customer_car_id)
            self.assertIsNone(reservation.car.contract)
            self.assertIsNone(reservation.car.matching_scheme)
            self.assertIsNone(reservation.car.matching_version)
            reservation = db.query(Reservation).filter(Reservation.id == "test5").first()
            self.assertIsNotNone(reservation)
            self.assertIsNotNone(reservation.start)
            self.assertTrue(isinstance(reservation.start, datetime.datetime))
            self.assertIsNotNone(reservation.end)
            self.assertTrue(isinstance(reservation.end, datetime.datetime))
            self.assertEqual("BARCODE", reservation.barcode)
            self.assertEqual(reservation.car.lpr_id, "RESERVATION2")
            self.assertEqual(reservation.car.lpr_search_id, access_utils.get_lpr_id_search("RESERVATION2"))
            self.assertEqual(reservation.car.lpr_country, "-")
            self.assertIsNone(reservation.car.customer_car_id)
            self.assertIsNone(reservation.car.contract)
            self.assertIsNone(reservation.car.matching_scheme)
            self.assertIsNone(reservation.car.matching_version)

        # delete all reservations
        set_request = KVSetRequest(service=self.kv_store_reservations.service_name, kvs=[
            KVSetRequestKV(key="test4", e_tag=None, previous_e_tag=4, value='null'),
            KVSetRequestKV(key="test5", e_tag=None, previous_e_tag=5, value='null'),
        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            self.assertEqual(0, db.query(Reservation).count())
            self.assertEqual(0, db.query(Car).count())
            self.assertEqual(0, db.query(Contract).count())

    def test_kv_store_update(self):
        self.setup_multi_kv_store()

        # contracts
        set_request = KVSetRequest(service=self.kv_store_contracts.service_name, kvs=[
            KVSetRequestKV(key="test1", e_tag=1, previous_e_tag=None,
                           value=dedent("""
                                   {
                                    "contract_id": "0000-FEED-0000-0001",
                                    "group_limit": 1,
                                    "access_infos": {
                                        "test": "test"
                                    },
                                    "cars": [
                                        {
                                            "customer_car_id": "car1",
                                            "license_plate": "G:TEST1",
                                            "country": "A",
                                            "matching_scheme": "DEFAULT",
                                            "matching_version": 20
                                        }
                                    ]
                                   }
                                   """)),
        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            self.assertEqual(1, db.query(Contract).count())
            self.assertEqual(1, db.query(Car).count())
        set_request = KVSetRequest(service=self.kv_store_contracts.service_name, kvs=[
            KVSetRequestKV(key="test1", e_tag=2, previous_e_tag=1,
                           value=dedent("""
                                           {
                                            "contract_id": "0000-FEED-0000-0002",
                                            "group_limit": 0,
                                            "access_infos": {},
                                            "cars": [
                                                {
                                                    "customer_car_id": "car2",
                                                    "license_plate": "LÖ:TEST1",
                                                    "country": "D",
                                                    "matching_scheme": "LEGACY",
                                                    "matching_version": 0
                                                }
                                            ]
                                           }
                                           """)),
        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            self.assertEqual(1, db.query(Contract).count())
            self.assertEqual(1, db.query(Car).count())
            contract = db.query(Contract).filter(Contract.id == "test1").first()
            self.assertEqual("0000-FEED-0000-0002", contract.contract_id)
            self.assertEqual(0, contract.group_limit)
            self.assertDictEqual({}, contract.access_infos)
            car = db.query(Car).filter(Car.lpr_search_id == access_utils.get_lpr_id_search("LÖ TEST1")).first()
            self.assertEqual("car2", car.customer_car_id)
            self.assertEqual("LÖ:TEST1", car.lpr_id)
            self.assertEqual("D", car.lpr_country)
            self.assertEqual("LEGACY", car.matching_scheme)
            self.assertEqual(0, car.matching_version)

        # we flush our database and test update for reservation
        with self.database as db:
            db.query(Car).delete()
            db.query(Contract).delete()

        set_request = KVSetRequest(service=self.kv_store_reservations.service_name, kvs=[
            KVSetRequestKV(key="test2", e_tag=3, previous_e_tag=None,
                           value=dedent("""
                                       {
                                        "start": "2023-09-05T17:57:12",
                                        "end": "2023-09-05T19:00:00",
                                        "barcode": "1CE1CE-BABY",
                                        "car": {
                                            "license_plate": "UNKNOWN1",
                                            "country": "-"
                                        }
                                       }
                                       """)),

        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            self.assertEqual(1, db.query(Reservation).count())
            self.assertEqual(1, db.query(Car).count())

        set_request = KVSetRequest(service=self.kv_store_reservations.service_name, kvs=[
            KVSetRequestKV(key="test2", e_tag=4, previous_e_tag=3,
                           value=dedent("""
                                       {
                                        "start": "2000-01-01T00:00:00",
                                        "end": "2023-12-31T23:59:59",
                                        "barcode": "PikaPika",
                                        "car": {
                                            "license_plate": "G:ASDF1",
                                            "country": "A"
                                        }
                                       }
                                       """)),

        ])
        self.rpc(channel="kv_sync", type="set", request=set_request, response_type=KVSetResponse)
        with self.database as db:
            self.assertEqual(1, db.query(Reservation).count())
            self.assertEqual(1, db.query(Car).count())
            reservation = db.query(Reservation).filter(Reservation.id == "test2").first()
            self.assertEqual(datetime.datetime(2000, 1, 1, 0, 0, 0), reservation.start)
            self.assertEqual(datetime.datetime(2023, 12, 31, 23, 59, 59), reservation.end)
            self.assertEqual("PikaPika", reservation.barcode)
            car = db.query(Car).filter(Car.lpr_search_id == "GASDF1").first()
            self.assertEqual(car.lpr_id, "G:ASDF1")
            self.assertEqual(car.lpr_country, "A")

    def test_kv_store_rpc_filtering(self):
        self.setup_multi_kv_store()

        # on run all stores should run in a thread

        # contracts
        with self.database as db:
            contract = Contract(contract_id="contractId", group_limit=1, access_infos={}, barcode=None, key="key1",
                                e_tag=1)
            car = Car(contract=contract, lpr_id="GTEST1", lpr_search_id="GTEST1", lpr_country="A")
            db.add(contract)
            db.add(car)
        response: KVSyncResponse = self.rpc("kv_sync", "sync",
                                            KVSyncRequest(service=self.kv_store_contracts.service_name, kvs={}),
                                            KVSyncResponse)
        self.assertEqual(1, len(response.additions.keys()))
        # reservation
        with self.database as db:
            reservation = Reservation(start=datetime.datetime.now(), end=datetime.datetime.now(), barcode="CODE",
                                      key="key2", e_tag=1)
            car = Car(reservation=reservation, lpr_id="GTEST1", lpr_search_id="GTEST1", lpr_country="A")
            db.add(reservation)
            db.add(car)
        response: KVSyncResponse = self.rpc("kv_sync", "sync",
                                            KVSyncRequest(service=self.kv_store_reservations.service_name, kvs={}),
                                            KVSyncResponse)
        self.assertEqual(1, len(response.additions.keys()))
        # unknown suffix, therefore RPC should not be answered, and it runs into a timeout
        with self.assertRaises(TimeoutError):
            self.rpc("kv_sync", "sync", KVSyncRequest(service="unknown_suffix", kvs={}), KVSyncResponse)

    def test_kv_store_start_and_shutdown(self):
        self.setup_multi_kv_store()

        # run should start all threads for the stores
        self.multi_store.run_as_thread()

        # we wait a little until multi kv store finished startup
        for _ in range(3):
            if not (self.multi_store.run_thread or self.multi_store.run_thread.is_alive()):
                time.sleep(0.1)
            else:
                break
        self.assertIsNotNone(self.multi_store.run_thread)

        # we check if all threads of the stores have started
        for store in self.multi_store.stores:
            for _ in range(3):
                if store.run_thread is None or not store.run_thread.is_alive():
                    time.sleep(0.1)
                else:
                    break
            self.assertIsNotNone(store.run_thread)

        # the shutdown function should kill all running instances of the stores
        self.multi_store.shutdown(timeout=1)
        time.sleep(1.1)
        self.assertFalse(self.multi_store.running)
        for store in self.multi_store.stores:
            self.assertFalse(store.running)
