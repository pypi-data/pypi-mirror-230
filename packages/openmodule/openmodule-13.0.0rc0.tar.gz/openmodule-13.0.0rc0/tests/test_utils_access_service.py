import os
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from unittest import TestCase

import freezegun
from dateutil.parser import parse
from settings_models.settings.common import Gate, GateType, ParkingArea, ShorttermLimitType, Parksetting
from sqlalchemy import Column, String, Integer, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from openmodule.config import settings
from openmodule.database.custom_types import JSONEncodedDict
from openmodule.database.database import Database
from openmodule.models.access_service import AccessCheckRequest, AccessTime, AccessCheckAccess, AccessCategory, \
    AccessRequestVehicle, AccessCheckResponse
from openmodule.models.vehicle import LPRMedium, LPRCountry, Medium, QRMedium
from openmodule.rpc.server import RPCServer
from openmodule.utils.access_service import AccessService, check_accesses_valid_at_gate, deduplicate_accesses, \
    check_accesses_valid_at_time, get_lpr_id_search, LPRKnownAccess, find_lpr_accesses
from openmodule.utils.kv_store import KVStore, KVEntry
from openmodule.utils.matching import MatchingConfig
from openmodule_test.access_service import AccessServiceWithSessionsTestMixin, TestAccessServiceWithSessions
from openmodule_test.core import OpenModuleCoreTestMixin
from openmodule_test.database import SQLiteTestMixin
from openmodule_test.eventlistener import MockEvent
from openmodule_test.rpc import RPCServerTestMixin
from openmodule_test.settings import SettingsMocker


class WithSessionsFunctionTest(AccessServiceWithSessionsTestMixin, TestCase):
    access_service_class = TestAccessServiceWithSessions

    def test_access(self):
        self.access_service_class.access_by_lpr = {"GARIVO2": dict(id="access-lpr", category=AccessCategory.permanent,
                                                                   accepted=True, access_data={},
                                                                   used_medium=Medium(type="lpr", id="GARIVO2"),
                                                                   access_infos={"medium_display_name": "qr"},
                                                                   source="test")}
        self.access_service_class.access_by_qr = {"qr1": dict(id="access-qr", category=AccessCategory.permanent,
                                                              accepted=True, access_data={},
                                                              used_medium=Medium(type="qr", id="qr1"),
                                                              access_infos={"medium_display_name": "qr"},
                                                              source="test")}


        vehicle = dict(lpr=dict(id="GARIVO1"))
        result = self.check_auth(vehicle)
        self.assertTrue(result.success)
        self.assertEqual([], result.accesses)

        result = self.check_auth(vehicle, gate="empty")
        self.assertTrue(result.success)
        self.assertEqual([], result.accesses)

        result = self.check_auth(vehicle, gate="error")
        self.assertFalse(result.success)
        self.assertEqual([], result.accesses)

        try:
            self.check_auth(vehicle, gate="exception")
        except Exception as e:
            self.assertEqual("test_exception", str(e))

        vehicle = dict(lpr=dict(id="GARIVO2"))
        result = self.check_auth(vehicle)
        self.assertTrue(result.success)
        self.assertNotEqual([], result.accesses)

        # nfc and pin is not supported and therefore will be ignored by the check access rpc
        vehicle = dict(pin=dict(id="pin1", type="pin"), qr=dict(id="qr1", type="qr"), nfc=dict(id="nfc1", type="nfc"))
        result = self.check_auth(vehicle)
        self.assertTrue(result.success)
        self.assertEqual(1, len(result.accesses))
        for x in result.accesses:
            self.assertIn(x.id, ["access-qr", "access-nfc", "access-pin"])


Base = declarative_base()


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


class TestAccessService(AccessService):
    def __init__(self, database: Database, settings_mocker: SettingsMocker,
                 matching_config: Optional[MatchingConfig] = None):
        self.database = database
        self.settings = settings_mocker
        self.matching_config = matching_config or settings.YAML.matching_config
        super().__init__()

    @staticmethod
    def db_model_to_access(db_model: TestAccessModelBase, used_medium: Medium) -> AccessCheckAccess:
        common_data = dict(id=db_model.id, group_id=db_model.group_id, customer_id=db_model.customer_id,
                           car_id=db_model.car_id, access_infos=db_model.access_infos or {}, source="test",
                           parksettings_id=db_model.parksettings_id, category=AccessCategory.whitelist)
        access_data = dict(matching_scheme=db_model.matching_scheme, matching_version=db_model.matching_version)
        return AccessCheckAccess(access_data=access_data, used_medium=used_medium, accepted=True, **common_data)

    def find_lpr_accesses(self, medium: LPRMedium) -> List[AccessCheckAccess]:
        # we query our database with cleaned lpr, because cleaned lpr should be an index field, and it is faster
        # as transforming our whole database to the list of objects needed for the find_lpr_accesses() utils function
        plate_clean = get_lpr_id_search(medium.id)
        with self.database as db:
            res = db.query(TestAccessModelBase).filter(TestAccessModelBase.lpr_id_search == plate_clean).all()
            # we transform data into a dict for faster creation of AccessCheckAccess models with correct access id
            res = {r.id: r for r in res}
            known_accesses = [LPRKnownAccess(id=a.id, lpr_id=a.lpr_id, lpr_country=a.lpr_country,
                                             matching_scheme=a.matching_scheme, matching_version=a.matching_version)
                              for a in res.values()]
            matched = find_lpr_accesses(medium, known_accesses, self.matching_config)
            return [self.db_model_to_access(res[m.id], Medium(type=medium.type, id=m.id)) for m in matched]

    def find_regex_accesses(self, medium: LPRMedium) -> List[AccessCheckAccess]:
        with self.database as db:
            regexes = db.query(TestAccessModelBase).filter(TestAccessModelBase.regex.isnot(None)).all()
            return [self.db_model_to_access(access, Medium(type="regex", id=access.regex))
                    for access in regexes if re.match(access.regex, medium.id)]

    def find_qr_accesses(self, medium: QRMedium) -> List[AccessCheckAccess]:
        with self.database as db:
            return [self.db_model_to_access(access, Medium(type="qr", id=access.qr_id))
                    for access in db.query(TestAccessModelBase).filter(TestAccessModelBase.qr_id == medium.id).all()]

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


class TestAccessKVStore(KVStore):
    database_table = TestAccessModelBase


class WithDatabaseFunctionTest(SQLiteTestMixin, OpenModuleCoreTestMixin):
    alembic_path = "../tests/test_access_service_database"
    database_name = "access_service"
    settings = SettingsMocker({})
    matching_config = MatchingConfig(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                            "resources/standard_schemes"))

    def setUp(self) -> None:
        super().setUp()
        self.access_service = TestAccessService(database=self.database, settings_mocker=self.settings,
                                                matching_config=self.matching_config)
        self.kv_store = TestAccessKVStore(db=self.database)

    def tearDown(self):
        super().tearDown()

    def test_find_lpr_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", lpr_id="G ARIVO 1", lpr_country="A", matching_version=40))
            db.add(TestAccessModelBase(id="2", lpr_id="G ARIVO1", lpr_country="B", matching_version=30,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="3", lpr_id="G:ARIVO1", lpr_country="CH", matching_version=20,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="4", lpr_id="GARIVO1", lpr_country="D", matching_version=20,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="5", lpr_id="GARIVO1", lpr_country="E",
                                       access_infos={}))  # is default 10
            db.add(TestAccessModelBase(id="6", lpr_id="GARIV01", lpr_country="F", matching_version=0,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="7", lpr_id="WARIV01", lpr_country="GR", matching_version=0,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="8", qr_id="QR1", access_infos={"medium_display_name": "qr"}))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="G ARIVO 1", country=LPRCountry(code="A")))
        self.assertEqual(5, len(accesses))
        self.assertEqual({"1", "2", "3", "5", "6"}, set([a.id for a in accesses]))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="GARIVO1"))
        self.assertEqual(3, len(accesses))
        self.assertEqual({"4", "5", "6"}, set([a.id for a in accesses]))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="GARIV Q 1"))
        self.assertEqual(1, len(accesses))
        self.assertEqual({"6"}, set([a.id for a in accesses]))

        # we do not support edit distance in the access util function
        with self.assertRaises(AssertionError):
            self.matching_config.edit_distance = 1
            accesses = self.access_service.find_lpr_accesses(LPRMedium(id="B ARIVQ 1"))

    def test_find_qr_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", qr_id="QR1", access_infos={"medium_display_name": "qr"}))
            db.add(TestAccessModelBase(id="2", qr_id="QR2", access_infos={"medium_display_name": "qr"}))
            db.add(TestAccessModelBase(id="3", qr_id="QR1", access_infos={"medium_display_name": "qr"}))
            db.add(TestAccessModelBase(id="4", qr_id="NFC1", access_infos={"medium_display_name": "qr"}))

        accesses = self.access_service.find_qr_accesses(QRMedium(type="qr", id="QR1"))
        self.assertEqual(2, len(accesses))
        self.assertEqual("1", accesses[0].id)
        self.assertEqual("3", accesses[1].id)
        self.assertEqual({"medium_display_name": "qr"}, accesses[1].access_infos)
        accesses = self.access_service.find_qr_accesses(QRMedium(type="qr", id="QR3"))
        self.assertEqual(0, len(accesses))

    def test_find_regex_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", regex="^.+RD$", access_infos={"medium_display_name": "regex"}))
            db.add(TestAccessModelBase(id="2", regex="^BP.+$", access_infos={"medium_display_name": "regex"}))
            db.add(TestAccessModelBase(id="3", regex="^BH.+$", access_infos={"medium_display_name": "regex"}))
            db.add(TestAccessModelBase(id="4", regex="^.+RD$", access_infos={"medium_display_name": "regex"}))
            db.add(TestAccessModelBase(id="5", qr_id="QR1", access_infos={"medium_display_name": "regex"}))

        accesses = self.access_service.find_regex_accesses(LPRMedium(type="lpr", id="BP 123 RD"))
        self.assertEqual(3, len(accesses))
        self.assertEqual("1", accesses[0].id)
        self.assertEqual("2", accesses[1].id)
        self.assertEqual("4", accesses[2].id)
        accesses = self.access_service.find_regex_accesses(LPRMedium(type="lpr", id="G ARIVO 1"))
        self.assertEqual(0, len(accesses))

    def test_deduplicate(self):
        accesses = [AccessCheckAccess(id=str(i), parksettings_id="1", access_data={}, accepted=True,
                                      category=AccessCategory.whitelist, used_medium=Medium(type="qr", id=""),
                                      access_infos={"medium_display_name": "qr"}, source="test")
                    for i in [1, 5, 3, 4, 2, 1, 2, 3, 4, 5]]
        accesses = deduplicate_accesses(accesses)
        self.assertEqual(["1", "5", "3", "4", "2"], [a.id for a in accesses])

    def test_gate_check(self):
        def create_access_dummy(id, parksettings_id, category):
            return AccessCheckAccess(id=id, parksettings_id=parksettings_id, access_data={}, accepted=True,
                                     category=category, used_medium=Medium(type="qr", id=""),
                                     access_infos={"medium_display_name": "qr"}, source="test")

        def create_access_dummies():
            return [create_access_dummy(id="1", parksettings_id=str(uuid.UUID(int=0)),
                                        category=AccessCategory.whitelist),
                    create_access_dummy(id="2", parksettings_id=str(uuid.UUID(int=1)),
                                        category=AccessCategory.whitelist),
                    create_access_dummy(id="6", parksettings_id=None, category=AccessCategory.whitelist),
                    create_access_dummy(id="11", parksettings_id=str(uuid.UUID(int=0)),
                                        category=AccessCategory.shortterm),
                    create_access_dummy(id="12", parksettings_id=str(uuid.UUID(int=1)),
                                        category=AccessCategory.shortterm),
                    create_access_dummy(id="16", parksettings_id=None, category=AccessCategory.shortterm)
                    ]

        self.settings.settings = {("common/gates", ""): {"gate1": Gate(gate="gate1", name="gate1", type=GateType.entry),
                                                         "gate2": Gate(gate="gate2", name="gate2", type=GateType.exit),
                                                         "gate3": Gate(gate="gate3", name="gate3", type=GateType.entry),
                                                         "door": Gate(gate="door", name="door", type=GateType.door)},
                                  ("common/parking_areas2", ""): {},
                                  ("common/parksettings2", ""): {}}

        # test door, all have access
        accesses = create_access_dummies()
        check_accesses_valid_at_gate(accesses, "door", self.settings)
        self.assertTrue(all(a.accepted for a in accesses))

        # test gate1, parksetting not found, parking_area not found
        accesses = create_access_dummies()
        check_accesses_valid_at_gate(accesses, "gate2", self.settings)
        self.assertEqual([True] * 3 + [False] * 3, [a.accepted for a in accesses])

        self.settings.settings[("common/parking_areas2", "")] = \
            {str(uuid.UUID(int=0)): ParkingArea(id=str(uuid.UUID(int=0)), name="pa0", gates=["gate1", "gate2"],
                                                shortterm_gates=["gate1"], default_cost_entries=[],
                                                shortterm_limit_type=ShorttermLimitType.no_limit, shortterm_limit=100)}

        # test gate1, parksetting not found, parking_area found and gate is shortterm gate
        accesses = create_access_dummies()
        check_accesses_valid_at_gate(accesses, "gate1", self.settings)
        self.assertTrue(all(a.accepted for a in accesses))

        # test gate2, parksetting not found, parking_area found and gate is not shortterm gate
        accesses = create_access_dummies()
        check_accesses_valid_at_gate(accesses, "gate2", self.settings)
        self.assertEqual([True] * 3 + [False] * 3, [a.accepted for a in accesses])

        self.settings.settings[("common/parksettings2", "")] = \
            {str(uuid.UUID(int=0)): Parksetting(id=str(uuid.UUID(int=0)), name="ps0", gates=["gate1"],
                                                default_cost_entries=[]),
             str(uuid.UUID(int=1)): Parksetting(id=str(uuid.UUID(int=1)), name="ps1", gates=["gate2"],
                                                default_cost_entries=[])
             }

        # test gate1, parksetting found, parking_area found and gate is shortterm gate
        # use parksetting also for shortterm if given
        accesses = create_access_dummies()
        check_accesses_valid_at_gate(accesses, "gate1", self.settings)
        self.assertEqual([True, False, True, True, False, True], [a.accepted for a in accesses])


class RpcTest(AccessServiceWithSessionsTestMixin, RPCServerTestMixin, TestCase):
    rpc_channels = ["access_service"]
    topics = ["access_service", "session", "healthz"]
    access_service_class = TestAccessServiceWithSessions

    def setUp(self):
        super().setUp()
        self.server = RPCServer(context=self.zmq_context())
        self.server.run_as_thread()
        self.access_service.register_rpcs(self.server)
        self.wait_for_rpc_server(self.server)

    def tearDown(self):
        self.server.shutdown()
        super().tearDown()

    def test_access_rpc(self):
        # only test if rpc is passed on to function, function is tested in previous TestCase
        request = AccessCheckRequest(gateway="gate", name=self.core.config.NAME,
                                     vehicle=dict(lpr=dict(id="medium_id", type="lpr")))
        response = self.rpc("access_service", "auth", request, AccessCheckResponse)
        self.assertEqual(True, response.success)
        self.assertIn(request, self.access_service.accessed)

    def test_session_check_in(self):
        self.send_session_start_message()
        self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_in))

        MockEvent.reset_all_mocks()
        with self.assertLogs() as cm:
            self.send_session_start_message(gate="error")
            self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_in))
        self.assertIn("Error in session check in", cm.output[0])

    def test_session_check_out(self):
        self.send_session_finish_message()
        self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_out))

        MockEvent.reset_all_mocks()
        with self.assertLogs() as cm:
            self.send_session_finish_message(gate="error")
            self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_out))
        self.assertIn("Error in session check out", cm.output[0])


class AccessTimeTest(TestCase):
    def test_start_end(self):
        now = datetime.utcnow()
        dt = timedelta(days=1)

        at = AccessTime(start=None, end=None)
        self.assertEqual(True, at.is_valid_at(now, "Europe/Vienna"))
        self.assertEqual(True, at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertEqual(True, at.is_valid_at(now - dt, "Europe/Vienna"))

        at = AccessTime(start=now - dt, end=now + dt)
        self.assertTrue(at.is_valid_at(now, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now - 2 * dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now + 2 * dt, "Europe/Vienna"))

        at = AccessTime(end=now + dt)
        self.assertTrue(at.is_valid_at(now, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - 2 * dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now + 2 * dt, "Europe/Vienna"))

        at = AccessTime(start=now - dt)
        self.assertTrue(at.is_valid_at(now, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + 2 * dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now - 2 * dt, "Europe/Vienna"))

    def test_is_valid_timezone_issue(self):
        at = AccessTime(start="2020-01-01 00:00", end="2020-01-01 04:00")

        with freezegun.freeze_time("2020-01-01 03:30"):
            self.assertTrue(at.is_valid_at(datetime.utcnow(), None))

    def test_is_valid_recurrent_start_end_recurrent(self):
        at = AccessTime(start="2000-01-01T00:00", end="2000-01-07T23:59",
                        recurrence="DTSTART:19990108T110000\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
                        duration=3600 * 9)  # from 12:00 to 21:00

        # before the start date
        self.assertFalse(at.is_valid_at(parse("1999-12-30T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("1999-12-31T13:00"), "Europe/Vienna"))  # FR

        # between start and end
        self.assertFalse(at.is_valid_at(parse("2000-01-01T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2000-01-02T13:00"), "Europe/Vienna"))  # SO
        self.assertTrue(at.is_valid_at(parse("2000-01-03T13:00"), "Europe/Vienna"))  # MO
        self.assertTrue(at.is_valid_at(parse("2000-01-04T13:00"), "Europe/Vienna"))  # TU
        self.assertTrue(at.is_valid_at(parse("2000-01-05T13:00"), "Europe/Vienna"))  # WE
        self.assertTrue(at.is_valid_at(parse("2000-01-06T13:00"), "Europe/Vienna"))  # TH
        self.assertTrue(at.is_valid_at(parse("2000-01-07T13:00"), "Europe/Vienna"))  # FR

        # Test the exact limits on friday
        self.assertFalse(at.is_valid_at(parse("2000-01-07T11:59:59+01:00"), "Europe/Vienna"))  # FR
        self.assertTrue(at.is_valid_at(parse("2000-01-07T12:00+01:00"), "Europe/Vienna"))  # FR
        self.assertTrue(at.is_valid_at(parse("2000-01-07T20:59:59+01:00"), "Europe/Vienna"))  # FR
        self.assertFalse(at.is_valid_at(parse("2000-01-07T21:00:00+01:00"), "Europe/Vienna"))  # FR

        # after the end date
        self.assertFalse(at.is_valid_at(parse("2000-01-08T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2000-01-09T13:00"), "Europe/Vienna"))  # FR

    def test_is_valid_recurrent_start_no_end_recurrent(self):
        at = AccessTime(start="2000-01-01T00:00", end=None,
                        recurrence="DTSTART:19990108T110000\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
                        duration=3600 * 9)  # from 12:00 to 21:00

        # before the start date
        self.assertFalse(at.is_valid_at(parse("1999-12-30T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("1999-12-31T13:00"), "Europe/Vienna"))  # FR

        # between start and end
        self.assertFalse(at.is_valid_at(parse("2000-01-01T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2000-01-02T13:00"), "Europe/Vienna"))  # SO
        self.assertTrue(at.is_valid_at(parse("2000-01-03T13:00"), "Europe/Vienna"))  # MO
        self.assertTrue(at.is_valid_at(parse("2000-01-04T13:00"), "Europe/Vienna"))  # TU
        self.assertTrue(at.is_valid_at(parse("2000-01-05T13:00"), "Europe/Vienna"))  # WE
        self.assertTrue(at.is_valid_at(parse("2000-01-06T13:00"), "Europe/Vienna"))  # TH
        self.assertTrue(at.is_valid_at(parse("2000-01-07T13:00"), "Europe/Vienna"))  # FR

        # years later
        self.assertFalse(at.is_valid_at(parse("2022-01-01T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2022-01-02T13:00"), "Europe/Vienna"))  # SO
        self.assertTrue(at.is_valid_at(parse("2022-01-03T13:00"), "Europe/Vienna"))  # MO
        self.assertTrue(at.is_valid_at(parse("2022-01-04T13:00"), "Europe/Vienna"))  # TU
        self.assertTrue(at.is_valid_at(parse("2022-01-05T13:00"), "Europe/Vienna"))  # WE
        self.assertTrue(at.is_valid_at(parse("2022-01-06T13:00"), "Europe/Vienna"))  # TH
        self.assertTrue(at.is_valid_at(parse("2022-01-07T13:00"), "Europe/Vienna"))  # FR

    def test_recurrence_during_dst_change(self):
        at = AccessTime(start="2000-01-01T00:00", end=None, user="test", category="booked-visitor",
                        recurrence="DTSTART:19990108T000000\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU",
                        duration=3600 * 3 + 1)  # from 01:00 to 04:00

        # normal day
        self.assertFalse(at.is_valid_at(parse("2021-03-27T00:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T01:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T01:59+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T03:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T04:00+01:00"), "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(parse("2021-03-27T05:00+01:00"), "Europe/Vienna"))  # this is the normal case
        self.assertFalse(at.is_valid_at(parse("2021-03-27T06:00+01:00"), "Europe/Vienna"))

        # from +01:00 to +02:00
        self.assertFalse(at.is_valid_at(parse("2021-03-28T00:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T01:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T01:59+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T03:00+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T04:00+02:00"), "Europe/Vienna"))
        # usually it goes only until 4 o'clock, but during dst change we add the hour to avoid conflicts
        self.assertTrue(at.is_valid_at(parse("2021-03-28T05:00+02:00"), "Europe/Vienna"))  # special case
        self.assertFalse(at.is_valid_at(parse("2021-03-28T06:00+02:00"), "Europe/Vienna"))

        # from +02:00 to +01:00
        self.assertFalse(at.is_valid_at(parse("2021-10-31T00:00+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T01:00+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T01:59+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T03:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T04:00+01:00"), "Europe/Vienna"))
        # usually it goes only until 4 o'clock, but during dst change we add the hour to avoid conflicts
        self.assertTrue(at.is_valid_at(parse("2021-10-31T05:00+01:00"), "Europe/Vienna"))  # special case
        self.assertFalse(at.is_valid_at(parse("2021-10-31T06:00+01:00"), "Europe/Vienna"))
