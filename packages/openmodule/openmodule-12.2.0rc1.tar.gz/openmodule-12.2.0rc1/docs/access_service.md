# Access Service

Inherit from either
 * Access Service: No session handling and no access sync
 * AccessServiceWithSessions: Session handling (check in, check out, errors) and no access sync
 * AccessServiceWithDatabase: With Access Sync and no session handling
 * AccessServiceWithDatabase and AccessServiceWithSessions: Session handling and access sync

## Access Service

1. Set `auth_request_request_model` to AccessCheckRequest or to your own AccessCheckRequest subclass with reduced data
2. Implement the `rpc_check_access` function and probably add some other custom stuff

## AccessServiceWithSessions

In addition to the Access Service stuff implement the session handling functions `check_in_session`, `check_out_session` and `check_out_session`

## AccessServiceWithDatabase

In addition to the Access Service stuff:
1. Create your own database model, which is a child of `AccessModelBase`. You can add additional fields there. 
This class has to implement parse_value, which gets the value as an object (Dict, List, ...) and has to return
a dict of key value for every database field you want to set
2. In your Access Service class set `database_table` to your database model class and implement `rpc_check_access`. 
See testcase in test_utils_access_service.py
