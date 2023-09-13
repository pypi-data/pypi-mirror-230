# OpenModule V2

Some additional documentation:

* [Openmodule Core](docs/core.md)
* [RPC Server / Client](docs/rpc.md)

## Changes

Breaking changes are annotated [here](docs/migrations.md).

To quickly check if your service is susceptible to a known issue have a look [here](docs/migrations.md).

## Coding Standard

For ARIVO developers we have defined a simple coding standard [here](docs/coding_standard.md)

## Features

The openmodule package provides a lot of features:

### Settings

The openmodule package uses a global lazy configuration `openmodule.config.settings`. This setting includes some
standard parameters defined in `openmodule.config.GlobalSettings` and parameters from a customizable module. To specify
the module you can call `settings.configure(module)` or you can set the environment variable `SETTINGS_MODULE`. Per
default settings looks for the `config` module (it also looks for the `tests/config` module first for test cases)

#### Setting functions

The framework also provides multiple functions for more complex behaviours:

* debug(): Returns true if working in a debug environment, i.e. `DEBUG=True` or not in docker and unknown version
* testing(): Returns true if the `TESTING` env variable is set
* database_folder(): Returns the default database folder, depending on testing() and debug()
* version(): Returns the version of the package
* resource(): Returns the auth resource
* dev_device(): Returns if the device is authenticated at the dev device server or not, useful for connecting to the
  correct dev/prod server
* config_yaml_path(): Returns either the env varibale `CONFIG_YAML`or the default value depending on the environment (
  testing, debug, prod)
* yaml(model, path=None): Returns the parsed yaml config based on the model and the path (default config_yaml_path())
* dist_folder(): Returns either the env variable `DIST_FOLDER` or the default value depending on the environment

#### Global variables

Some variables are already mapped and usable by default. These settings can be used normally and can also be overwritten

```python
class GlobalSettings:
    # usual
    NAME = string("NAME", "om_dev_unnamed_1")
    VERSION = version()
    RESOURCE = resource()
    DEBUG = debug()
    TESTING = testing()
    LOG_LEVEL = log_level()
    DATABASE_FOLDER = database_folder()

    # broker env vars
    BROKER_SUB = broker_sub()
    BROKER_PUB = broker_pub()

    LOCAL_DEVELOPMENT = bool("LOCAL_DEVELOPMENT", False)
    is_bridged_slave = is_bridged_slave()
    DIST_FOLDER = dist_folder()
    DEV_DEVICE = dev_device()

    # redis
    REDIS_HOST = string("REDIS_HOST", "localhost")
    REDIS_PASSWORD = string("REDIS_PASSWORD", "") or None
    REDIS_PORT = int("REDIS_PORT", 6379)
    REDIS_DB = int("REDIS_DB", 0)
```

#### Examples of usage

```python
HOST_URL = "https://operator.arivo.fun" if dev_device() else "https://operator.arivo.app"


class YAMLConfig(OpenModuleModel):
    test: bool


YAML = config.yaml(YAMLConfig)
```

#### Models

Inherit from `OpenModuleModel` or in case of ZMQ messages from `ZMQMessage`. Models use
pydantic ([docs](https://pydantic-docs.helpmanual.io/usage/types/)), check openmodule.models.* for some examples (e.g.
PresenceBaseMessage for alias)

### Core

The base of the new openmodule, every package should have exactly one. The core handles various things:

* sentry
* logging
* dsvgo
* messaging
* health
* alerting
* database

``` python
core = init_openmodule(config, **kwargs)
shutdown_openmodule()
```

#### Messaging

##### Receiving messages

The core handles message distribution with a dispatcher. You only need to register your callback.

* **register_schema**: Automatically create a schema for your message handler and its models -> Beware that you need to
  document your handler method

```python
core.messages.register_handler("topic", MessageClass, callback, filter={type = "demo"}, register_schema = True)
```

It may also be used together with an event listener to provide further functionality

```python
event_listener = EventListener(log=logger)
core.messages.register_handler("topic", MessageClass, event_listener, filter={type = "demo"})
...
event_listener.append(some_function)
```

#### Sending messages

It is even easier to send messages

```python
message = ZMQMessage(name=core.config.NAME, type="demo")
core.publish(message, "topic")
```

#### Health

Due to the new convention, the health message should only represent if the service is still alive. This is done
automatically by the core. If you need to specify some meta data or errors you can pass your handler to the core or set
it later

```python
def healthy() -> HealthResult:
    if error:
        return health_error("we have an error", meta=dict(error="error"))
    return health_ok(meta=dict(this="is_easy"))


core = init_openmodule(config, health_handler=healthy)
# or
core.health.health_hanlder = healthy
```

#### Alerting

The new core also includes an alert handler.

```python
core.alerts.send(...)
alert_id = core.alerts.get_or_add_alert_id(...)
core.alerts.send_with_alert_id(alert_id, ...)
```

#### Database

The openmodule package now also feature a simple database which can be also specified during the template creation. If
you missed it there, just copy the directory src/database from the template. For more infos see [here](docs/database.md)

### RPCs

A new RPC server/client was implemented. It works like before and also includes better filtering:

* if a channel is provided for a filter, only rpcs of that channel will be subject to that filter
* if a type is provided for a filter, only rpcs of that type will be subject to that filter
* **register_schema**: Automatically create a schema for your rpc and its models -> Beware that you need to document
  your handler method

```python
def handler(request: AccessRequest):
    """
    awesome description
    """


rpc = RPCServer(config=core.config, context=core.context)
rpc_server.add_filter(self._backend_filter, "backend", "auth")
rpc_server.register_handler("backend", "auth", request_class=AccessRequest,
                            response_class=AccessResponse, handler=handler, register_schema=True)
rpc.run()
```

### Utils

#### Api (**DEPRECATED**)

We implemented a very basic Api class you can use for http request and that handles errors and authentication. Either
inherit it or create a class.

```python
api = Api(**kwargs)
try:
    res = api.post("some_url", payload=stuff)
except ApiException as e:
    if e.retry:  # <- makes sense to try again - timeouts or server not available ...
        ...
```

#### Backend (**DEPRECATED**)

There is also a basic implementation of a backend that provides registration and message passing.

```python
class MyAccessService(AccessService):
    def __init__(self):
        super().__init__(implements_session_handling=...)
        ...

    def rpc_check_access(self, request: AccessRequest) -> AccessCheckResponse:
        ...

    # session handling
    def check_in_session(self, message: SessionStartMessage):
        ...

    def check_out_session(self, message: SessionFinishMessage):
        ...

    def session_error_message(self, message: Union[SessionDeleteMessage, SessionIncompleteMessage,
                                                   SessionExitWithoutEntryMessage]):
        ...
```

#### Access Service

#### Charset

Useful functions for character manipulation

#### Connection Status

Helper class that checks the connection status of the rpc client to our server:

see [here](docs/connection_status_listener.md)

#### Matching

Useful functions for license plate matching

#### Presence

Helper class for listening to presence messages.

```python
presence_listener = PresenceListener(core.messages)
presence_listener.on_enter.append(some_function)
```

#### Package Reader

See [Package Reader](docs/package_reader.md).

#### Bridged Slave/Master Detection

Some services should behave differently if they are started on a bridged master device or bridged slave device (i.e.
prevent double rpc-responses, prevent double code execution).
For this each NUC is setup with a COMPUTE_ID.
The master NUC always has `COMPUTE_ID=1`. For easier detection the functions `is_bridged_slave()`
and `is_bridged_master()` are available.

##### Config

* The `COMPUTE_ID` env variable is responsible for the slave/master detection. Per default the COMPUTE_ID is set
  to `COMPUTE_ID=1`, therefore a master NUC.
* If you want to switch to a "slave" NUC, you can either set it directly with the env variable or override it for test
  cases (@override_settings(COMPUTE_ID=2))

##### Example

The DSGVO container takes care of the anonymization. For this it saves links between vehicle_ids and session_ids and
forwards requests to anonymize session_ids with the appropriate vehicle_ids.
If we have a bridged installation only the master DSGVO container should perform these tasks. The DSGVO container on
slave devices should only anonymize data on its device.

* RPC for anonymization and linking session to vehicle only registered `if is_bridged_slave() is False`

### Anonymization

The openmodule framework uses rpc requests and messages to trigger the anonymization of data.

* **Message:** You can send a AnonymizeMessage (topic: `privacy`). The message includes a session_id and vehicle_ids to
  delete.
* **RPC Request:** You can send an AnonymizeRequest with channel=`privacy`, type=`anonymize` to the DSGVO container.
  This request only includes session_ids.
  The DSGVO container will then match vehicle_ids to the session_ids and redistribute the request with the prior
  mentioned message.

A container with sensible data then needs to implement the message listener for the privacy messages (see example)

##### Example 1

The controller checked that a parking session was finished an fully paid. After a specified time, the DSGVO relevant
data has to be anonymized. The controller then triggers the anonymization

```python
request = AnonymizeRequest(session_ids=[session_id])
result = core.rpc_client.rpc("privacy", "anonymize", request)
if result.response.status == "ok":
    self.log.info(f"Anonymized session {session_id}")
```

##### Example 2

The controller checked that a parking session was finished an fully paid. After a specified time, the DSGVO relevant
data has to be anonymized. The controller then triggers the anonymization

```python
msg = AnonymizeMessage(vehicle_ids=[vid1, vid2])
self.core.publish(msg, "privacy")
```

The DSGVO container receives the request, matches session_ids with vehicle_ids and publishes the anonymization message.
It also listens on said messages an deletes vehicle images based on the vehicle_ids in the message.

```python
core.messages.register("privacy", AnonymizeMessage, anonymize_data)


def anonymize_data(message: AnonymizeMessage):
    for vid in message.vehicle_ids:
        delete_vehicle_image_by_vehicle_id(vid)
```

**IMPORTANT** You still have to take care of data retention in each service separately, meaning you have to delete data
independently of these anonymization messages.
i.e. the DSGVO service deletes data if we need disk space or the eventlog deletes events after 30 days by default


### Databox Upload

In the openmodule we have a utils function to simplify the upload with the databox service. The prerequisite is, 
that the upload folder `/data/om_service_databox_1/upload` is mounted correctly in the compose file to the `settings.DATABOX_UPLOAD_DIR` (default: `/upload`)

```python
from openmodule.utils.databox import upload

upload("/tmp/asdf.txt", "/enforcement/test/asdf.txt")
upload("/tmp/bsdf.csv", "exports/")  # same as exports/bsdf.csv as filename is taken from source if dst ends with /
```

docker-compose.yml example snippet
```yaml
    volumes:
    - /data/om_service_databox_1/upload/:/upload/
```

### CSV Export

In the openmodule we have a utils function to simplify the generation of csv files. 
For more infos see [here](docs/csv_export.md)


### Scheduling of jobs

See [here](https://github.com/ts-accessio/schedule/tree/dateutil-support)
Do not import `schedule` yourself, openmodule imports the schedule version with dateutil support for you. 


## Documentation

Openmodule >= 3.0.5 features automatic generation of Rpc and Message Schemas including their models. The generation uses
data that is generated during the test runs to create an OpenApi Schema. Your RPCs and Message handlers are
automatically documented if:

* You use the message dispatcher of the core (OpenModuleCoreTestMixin)
* You use the RPCServer of Openmodule

You can also register models yourself if you want them documented, but you may need to save the Schema in this case:

```python
from openmodule.utils.schema import Schema

Schema.save_model(Model)
Schema.save_rpc(channel, type, request, reqponse, handler)
Schema.save_message(topic, message_class, handler, filter)

Schema.to_file()
```

With default parameters, you need to document your handler functions with a doc string, that is then included as a
description.

## Testing

A separate package for testing openmodule packages exists within openmodule - openmodule-test. For more infos
see [here](docs/testing.md)

## Commands

A separate package for commands useful for developing openmodule package exists within openmoduel - openmodule-commands.
The commands will be automatically available if you installed the package

For a full list of the commands see [here](docs/commands.md)

## Installing from Git

During development it might be necessary to install a version of openmodule, where no pip package exists.
Below you can find how to install a certain openmodule branch for your application with pip:

* **openmodule:** `pip install "git+https://gitlab.com/arivo-public/device-python/openmodule@<branch>#egg=openmodule"`
* **
  openmodule-test:** `pip install "git+https://gitlab.com/arivo-public/device-python/openmodule@<branch>#egg=openmodule-test&subdirectory=openmodule_test"`
* **
  openmodule-commands:** `pip install "git+https://gitlab.com/arivo-public/device-python/openmodule@<branch>#egg=openmodule-commands&subdirectory=openmodule_commands"`
