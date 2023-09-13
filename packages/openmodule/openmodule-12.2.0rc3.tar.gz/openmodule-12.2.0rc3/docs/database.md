# Database

On the device we use `sqlalchemy` for our database. Additionally we use `alembic` for our migrations. An example of a
database is included in openmodule-test

## Models

### Definition

All database models inherit a `Base` from `sqlalchemy` and need an unique id.

```python
import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatabaseTestModel(Base):
    __tablename__ = "test"
    id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    value = Column(Integer, default=1)
    string = Column(String, default="initial")
```

### Registration

#### Models

All database models you want to use need to registered. This happens in the `src/database/alembic/env.py` file. Simply
list all used Bases in the register_bases function.

```python
from database.database_models import Base
from somewhere import Base as some_base

register_bases([Base, some_base])
```

#### Custom Column Types

You can also define custom column types, but they must inherit CustomType from `openmodule.database.custom_types` or
else there will be import errors in the migrations

```python
class TZDateTime(CustomType):
    impl = DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            assert value.tzinfo is None, "You need to convert a datetime to a naive time, because sqlite loses tz infos"
        return value
```

## Migrations

### Generating migrations

To generate the migration use the provided script `src/database/makemigration.sh` with a name for your migration.

```shell script
./makemigrations -m <name>
```

Afterwards the migrations are created under `src/database/alembic/versions`.

### Wo how to migrate

The database is always automatically migrated on creation of any database object in the program.

### Migration Examples

The alembic documentation already has some migration examples and tutorials, but here are some quick tips and pitfalls we have encountered.

**Renaming Columns**

When you rename a column, alembic usually creates a new column and drops the old one. It does not know whether you actually want a new 
column or want to rename the old one. This is why for renaming you usually have to write your own migration instead of auto generating it.

```python
# correct way: renames the column, keeps the data
def upgrade():
    op.pre_upgrade()

    with op.batch_alter_table('my_table_name', schema=None) as batch_op:
        batch_op.alter_column( "old_column", new_column_name="new_column")

    op.post_upgrade()
```

The wrong (auto-generated) migration would look like this. In the best case it would result in a null constraint error, but in the worst
case it would leave a empty column behind with all null values and you never notice until its too late.

```python
# WRONG WAY! drops the column, deletes the data and creates a new empty column
def upgrade():
    op.pre_upgrade()
    
    with op.batch_alter_table('my_table_name', schema=None) as batch_op:
        batch_op.add_column(sa.Column('new_column', sa.Integer(), nullable=True))
        batch_op.drop_column('old_column')

    op.post_upgrade()
```


### Avoiding broken database after failed migration

A failed migration might lead to a broken state where no migration is possible anymore. To avoid / fix this the
op.pre_upgrade() operation deletes all temporary tables from alembic. Intern the op.pre_upgrade()
calls `openmodule.database.drop_alembic_tmp_tables`

```python
def upgrade():
    op.prep_upgrade()
    ${upgrades if upgrades else "pass"}
```

### Foreign key constraints during migrations

Foreign key constraints are disabled during migrations, meaning you could possibly end up with rows referencing a
non-existing row. This only happens if manually written code messes this up. Alembic's operations should not cause such
a state, but due to limitations in sqlite foreign key constraints are disabled during migrations, because they cannot be
turned back on in the middle of a migration.

Foreign key constraints are disabled during `op.pre_upgrade()`.

## Database Access

To access the database we have to create our own instance, you can also pass the parameter `database=True` to the core
for it to create a database:
Then we can create a session an access the database.

```python
database = Database(**kwargs)
with database as db:
    do_stuff(db, ...)
```

If an exception is raised during an open database session, all changes will be rolled back.  
It is also possible to create multiple database within a program, but the need to is quite questionable.

## Basic db stuff

Normally sqlalchemy functions should suffice for most jobs. We implemented some additional functionality as functions
under `openmodule.utils.db_helper`.

### create

* db.add(model: DatabaseModel)
* db.add_all(models: List[DatabaseModel])

### query

* base_query = db.query(DatabaseModel)
* query = base_query..filter_by(**kwargs)
* query.all() returns a list

### query single object

* instance = query.one() -> returns element or raises exception if query has more or no elements (MultipleResultsFound,
  NoResultFound)
* instance = query.first() -> returns first element of query or None

### update

* db.add(model: DatabaseModel) -> previously created model
* db_helper.update_query(db, query, values: dict)

### delete

* db.delete(model: DatabaseModel)
* db_helper.delete_query(db, query)

### Useful query stuff

* order_by(*args) -> ordering
* yield_by(int) -> for batch processing
* distinct(*args) -> distinct


# Key-Value Store

The key-value store `openmodule.utils.kv_store.KVStore` interacts with the database to create a key-value store that is kept in 
sync with an external Server (RPC Server). **Services must not create/edit/delete the key-value entries themselves. 
They must only be created/edited/deleted by the provided rpcs that are called by the server.** (`channel=kv_store`). 
The database model needs to be created by the service by inheriting from the `openmodule.utils.kv_store.KVEntry`. 
Getter methods need to be implemented in the service. The `KVStore.sync_with_server()` method needs to be called on 
startup and reconnect. The set request is structured so that a value=None will delete the entry.

### KVEntry

* Must be inherited
* `key` and `e_tag` columns must not be changed
* Additional columns should be created.
* The `parse_value(value) -> dict` method needs to be implemented. 
  * It is called when a before a new entry is created.
  * Should parse the value (as sent by the external source) into the additional columns.
  * Returns a dict of {column_name: value} that will be used to create the entry.

### Syncing

* `KVStore.sync_with_server()` needs to be called on startup and reconnect.
  * To detect reconnects, use the `core.connection_listener`.
  * This method returns an `RPCClient.RPCEntry` that can be used to wait for the sync to finish.
* `KVStore.log_sync_rpc_response(rpc_entry: RPCClient.RPCEntry) -> Optional[ServerSyncResponse]` can be used to wait 
for the rpc to finish and log the response

### Notification on entry changed

* Inherit from `KVStoreWithChangedNotification`
* Implement `_get_comparison_values` and `_send_changed_notification` (needs check for if changed, most likely use 
  `_find_changed_kvs`)
* Implement a meaningful `comparison_value` function for your Database Model
