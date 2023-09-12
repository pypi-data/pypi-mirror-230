import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Set, List

from settings_models.settings.common import GateType

from openmodule.core import core
from openmodule.dispatcher import EventListener, MessageDispatcher
from openmodule.models.base import Gateway
from openmodule.models.presence import PresenceBaseMessage, PresenceBackwardMessage, PresenceForwardMessage, \
    PresenceChangeMessage, PresenceLeaveMessage, PresenceEnterMessage, PresenceRPCRequest, PresenceRPCResponse
from openmodule.models.vehicle import Vehicle
from openmodule.utils.charset import CharsetConverter, legacy_lpr_charset
from openmodule.utils.settings import SettingsProvider


def vehicle_from_presence_message(message: PresenceBaseMessage):
    return Vehicle(
        id=message.vehicle_id,
        lpr=message.medium.lpr,
        qr=message.medium.qr,
        nfc=message.medium.nfc,
        pin=message.medium.pin,
        make_model=message.make_model,
        all_ids=message.all_ids,
        enter_direction=message.enter_direction
    )


class VehicleDeduplicationData:
    lp_converter = CharsetConverter(legacy_lpr_charset)

    def __init__(self, vehicle: Vehicle, present_area_name: str, timeout: datetime):
        self.plate = VehicleDeduplicationData.lp_converter.clean(vehicle.lpr.id or "")
        self.present_area_name = present_area_name
        self.timeout = timeout
        self.drop_list = set()  # store here which vehicles should be dropped even after timeout
        self.dont_drop_list = set()  # store here which vehicles already caused message and thus should not be dropped

    def update_drop_list(self, message: PresenceBaseMessage, vehicle: Vehicle):
        not_in_drop_list = vehicle.id not in self.dont_drop_list
        within_timeout = datetime.utcnow() < self.timeout
        vehicle_has_no_media_or_has_same_plate = \
            not vehicle.has_media() or (vehicle.lpr and self.plate == self.lp_converter.clean(vehicle.lpr.id or ""))
        from_different_present_area = message.present_area_name != self.present_area_name
        drop = not_in_drop_list and within_timeout and self.plate and vehicle_has_no_media_or_has_same_plate and \
               from_different_present_area
        if drop:
            self.drop_list.add(vehicle.id)
        elif not vehicle_has_no_media_or_has_same_plate:
            self.dont_drop_list.add(vehicle.id)
            # only relevant on change as vehicle cannot already be on drop list on enter
            # and we should not undrop on leave/forward/backward
            if message.type == "change":
                self.drop_list.discard(vehicle.id)

    def should_deduplicate(self, vehicle: Vehicle):
        return vehicle.id in self.drop_list

    def should_cleanup(self):
        return self.timeout + timedelta(hours=1) < datetime.utcnow()


class PresenceListener:
    on_forward: EventListener[Tuple[Vehicle, Gateway]]
    on_backward: EventListener[Tuple[Vehicle, Gateway]]
    on_enter: EventListener[Tuple[Vehicle, Gateway]]
    on_leave: EventListener[Tuple[Vehicle, Gateway]]
    on_change: EventListener[Tuple[Vehicle, Gateway]]

    present_vehicles: Dict[str, Vehicle]
    # keys are vehicle ids to drop, value are if drop caused by a vehicle with medium
    # can be shared over all gates (if there are multiple gates) as vehicle id is unique
    drop_list: Dict[int, bool]
    drop_mapping: Dict[int, int]  # Dict from vehicle causing drop to dropped vehicle
    area_name_of_present: Dict[str, str]
    # List because there can be a new one before we are allowed to remove the old one
    last_vehicle_data: Dict[str, List[VehicleDeduplicationData]]
    pending_fw_bw: Set[int] = set()  # vehicle ids for which we are waiting for a forward or backward message

    @property
    def present_vehicle(self) -> Optional[Vehicle]:
        assert self.gate is not None, (
            "`.present_vehicle` may only be used when listening for a specific gate, this presence listener"
            "listens to all gates, please access the present vehicle per gate via `.present_vehicles[gate]`"
        )
        return self.present_vehicles.get(self.gate)

    def __init__(self, dispatcher: MessageDispatcher, gate: Optional[str] = None,
                 deduplication_timeout: timedelta = timedelta(seconds=10)):
        assert not dispatcher.is_multi_threaded, (
            "you cannot use a multithreaded message dispatcher for the presence listener. It is highly reliant "
            "on receiving messages in the correct order!"
        )
        self.log = logging.getLogger(self.__class__.__name__ + (" " + gate if gate else ""))
        self.on_forward = EventListener(log=self.log)
        self.on_backward = EventListener(log=self.log)
        self.on_enter = EventListener(log=self.log)
        self.on_change = EventListener(log=self.log)
        self.on_leave = EventListener(log=self.log)
        self.present_vehicles = dict()
        self.drop_list = dict()
        self.drop_mapping = dict()
        self.area_name_of_present = dict()
        self.last_vehicle_data = dict()
        self.deduplication_timeout = deduplication_timeout
        self.gate = gate

        dispatcher.register_handler("presence", PresenceBackwardMessage, self._on_backward)
        dispatcher.register_handler("presence", PresenceForwardMessage, self._on_forward)
        dispatcher.register_handler("presence", PresenceChangeMessage, self._on_change)
        dispatcher.register_handler("presence", PresenceLeaveMessage, self._on_leave)
        dispatcher.register_handler("presence", PresenceEnterMessage, self._on_enter)

    def init_present_vehicles(self, settings_provider: Optional[SettingsProvider] = None):
        if self.gate is None:
            gates = []
            try:
                settings_provider = settings_provider or SettingsProvider(rpc_timeout=1.0)
                gates = settings_provider.get("common/gates")
                gates = [gate_id for gate_id, gate in gates.items() if gate.type != GateType.door]
            except TimeoutError:
                self.log.error("Gate is None and could not get gates (timeout)")
            except Exception as e:
                self.log.exception("Gate is None and could not get gates")
        else:
            gates = [self.gate]

        reqs = {}
        for gate in gates:
            reqs[gate] = core().rpc_client.rpc_non_blocking("tracking", "get-present", PresenceRPCRequest(gate=gate))
        for gate, request in reqs.items():
            try:
                result = request.result(PresenceRPCResponse)
                if result.presents:
                    self._on_enter(result.presents[0])
            except TimeoutError:
                self.log.error("get-present RPC timeout", extra={"gate": gate})
            except Exception as e:
                self.log.exception("get-present RPC error", extra={"gate": gate})

    def _gate_matches(self, message: PresenceBaseMessage):
        return (self.gate is None) or (message.gateway.gate == self.gate)

    def _drop_check(self, message: PresenceBaseMessage, vehicle: Vehicle):
        gate = message.gateway.gate
        # execute this on every presence message
        for x in self.last_vehicle_data.get(gate, []):
            x.update_drop_list(message, vehicle)
        present_vehicle = self.present_vehicles.get(gate)

        # only drop when in drop list either has no medium or dropped because of vehicle with media
        # (no present means old present was completely processed)
        # also no present_area_name check as vehicle cannot be on drop list if its from the same present area
        if vehicle.id in self.drop_list and (self.drop_list[vehicle.id] or not vehicle.has_media()):
            return True
        elif present_vehicle:
            # some present area -> no drop, use old behavior (simulate leave for enter messages, otherwise just replace)
            if self.area_name_of_present.get(gate, "") == message.present_area_name:
                return False
            # this prevents dropping delayed forward or backward messages if next vehicle is already present
            elif vehicle.id in self.pending_fw_bw:
                return False
            # new vehicle is better, simulate leave for old vehicle and remove new vehicle from drop list and add old
            elif not present_vehicle.has_media() and vehicle.has_media():
                self.log.warning("Got better vehicle from another present area. A leave will be faked for the old "
                                 "vehicle to get a consistent setup for the new vehicle.",
                                 extra={"present_vehicle": str(present_vehicle),
                                        "new_vehicle": str(vehicle)})
                self.drop_list.pop(vehicle.id, None)  # discard because vehicle might be in drop list
                self.drop_list[present_vehicle.id] = True  # has media
                self.drop_mapping[vehicle.id] = present_vehicle.id
                self.present_vehicles.pop(gate, None)
                self.on_leave(present_vehicle, message.gateway)
                return False
            # different present area and new vehicle is not better -> drop
            else:
                self.drop_list[vehicle.id] = present_vehicle.has_media()
                self.drop_mapping[present_vehicle.id] = vehicle.id
                return True
        # here we handle case that same vehicle is first seen by camera 1 and after leave seen by camera 2
        elif any([x.should_deduplicate(vehicle) for x in self.last_vehicle_data.get(gate, [])]):
            return True
        else:
            return False

    def _cleanup_drop_list(self):
        # this assumes vehicle id is UTC timestamp in nanoseconds (which is the case unless someone changes Tracking)
        self.drop_list = {k: v for k, v in self.drop_list.items() if k / 1e9 > time.time() - 3600}

    def _fake_leave_if_missing(self, message: PresenceBaseMessage):
        present_vehicle = self.present_vehicles.get(message.gateway.gate)
        if present_vehicle and present_vehicle.id == message.vehicle_id:
            self.log.error(f"Got {message.type} without a leave. We generate a leave ourself.")
            self._on_leave(PresenceLeaveMessage(**message.dict()))

    def _on_backward(self, message: PresenceBackwardMessage):
        """
        This handler forwards presence backward  messages to the registered calls in the presence listener
        """

        if not self._gate_matches(message):
            return
        vehicle = vehicle_from_presence_message(message)
        drop_message = self._drop_check(message, vehicle)
        self.drop_list.pop(vehicle.id, None)
        if drop_message:
            return

        self._fake_leave_if_missing(message)

        self.log.debug("presence backward: %s", vehicle)
        self.on_backward(vehicle, message.gateway)
        self.pending_fw_bw.discard(vehicle.id)

    def _on_forward(self, message: PresenceForwardMessage):
        """
        This handler forwards presence forward messages to the registered calls in the presence listener
        """
        if not self._gate_matches(message):
            return
        vehicle = vehicle_from_presence_message(message)
        drop_message = self._drop_check(message, vehicle)
        self.drop_list.pop(vehicle.id, None)
        if drop_message:
            return

        self._fake_leave_if_missing(message)

        self.log.debug("presence forward: %s", vehicle)
        self.on_forward(vehicle, message.gateway)
        self.pending_fw_bw.discard(vehicle.id)

    def _on_leave(self, message: PresenceLeaveMessage):
        """
        This handler forwards presence leave messages to the registered calls in the presence listener
        and clears the present vehicle
        """

        if not self._gate_matches(message):
            return
        leaving_vehicle = vehicle_from_presence_message(message)
        if self._drop_check(message, leaving_vehicle):
            return

        self.log.debug("presence leave: %s", leaving_vehicle)
        present_vehicle = self.present_vehicles.get(message.gateway.gate)
        if present_vehicle:
            if present_vehicle.id != leaving_vehicle.id:
                self.log.error("A vehicle left with a different vehicle id than the present one. Tracking is "
                               "inconsistent. We are fake-leaving the currently present vehicle, to ensure consistent "
                               "states.", extra={"present_vehicle": str(present_vehicle),
                                                 "leaving_vehicle": str(leaving_vehicle)})
            self.present_vehicles.pop(message.gateway.gate, None)
            self.area_name_of_present.pop(message.gateway.gate, None)
            self.pending_fw_bw.add(leaving_vehicle.id)
            self.on_leave(leaving_vehicle, message.gateway)

            # cleanup last_vehicle_data and drop list
            self.last_vehicle_data[message.gateway.gate] = \
                [x for x in self.last_vehicle_data.get(message.gateway.gate, []) if not x.should_cleanup()]
            self._cleanup_drop_list()

            if leaving_vehicle.lpr:
                self.last_vehicle_data[message.gateway.gate].append(
                    VehicleDeduplicationData(leaving_vehicle, message.present_area_name,
                                             datetime.utcnow() + self.deduplication_timeout))
        else:
            self.log.error("A vehicle left while non was previously present. Tracking is inconsistent. "
                           "The leave will be ignored, to ensure consistent states.",
                           extra={"leaving_vehicle": str(leaving_vehicle)})

    def _on_enter(self, message: PresenceEnterMessage):
        """
        This handler forwards presence enter messages to the registered calls in the presence listener
        and sets the present vehicle
        """

        if not self._gate_matches(message):
            return
        new_vehicle = vehicle_from_presence_message(message)
        if self._drop_check(message, new_vehicle):
            return

        self.log.debug("presence enter: %s", new_vehicle)
        present_vehicle = self.present_vehicles.get(message.gateway.gate)
        if present_vehicle:
            self.log.error("A new vehicle entered while one was still present. Tracking is inconsistent. "
                           "A leave will be faked, to ensure consistent states.",
                           extra={"present_vehicle": str(present_vehicle),
                                  "new_vehicle": str(new_vehicle)})
            self.on_leave(present_vehicle, message.gateway)

        self.present_vehicles[message.gateway.gate] = new_vehicle
        self.area_name_of_present[message.gateway.gate] = message.present_area_name
        self.on_enter(new_vehicle, message.gateway)

    def _on_change(self, message: PresenceChangeMessage):
        """
        This handler forwards presence change messages to the registered calls in the presence listener
        and changes the present vehicle
        """

        if not self._gate_matches(message):
            return
        vehicle = vehicle_from_presence_message(message)
        if self._drop_check(message, vehicle):
            return

        change_with_vehicle_present = message.gateway.gate in self.present_vehicles
        if change_with_vehicle_present and self.present_vehicles[message.gateway.gate].id != vehicle.id:
            self.log.debug("vehicle_id changed in presence change: %s. "
                           "Faking leave and triggering presence enter!", vehicle)
            self.on_leave(self.present_vehicles[message.gateway.gate], message.gateway)
            change_with_vehicle_present = False

        self.present_vehicles[message.gateway.gate] = vehicle
        self.area_name_of_present[message.gateway.gate] = message.present_area_name
        if change_with_vehicle_present:
            self.log.debug("presence change: %s", vehicle)
            self.on_change(vehicle, message.gateway)
        else:
            self.log.warning("presence enter triggered by change: %s", vehicle)
            self.on_enter(vehicle, message.gateway)
