import logging
import json
import typing

import tenacity
import logging

from urllib.parse import urljoin
from datetime import datetime, timezone

from .commands.proc import Proc
from .commands.netstat import Netstat
from .. import constants
from .. import contrib
from collections import defaultdict

if typing.TYPE_CHECKING:
    from typing import Callable, Text


log = logging.getLogger("agent")


DISABLED = 0
DISCOVERY_MODE = 1
ALERT_MODE = 2


class SecurityExtensions:
    """Manages security extensions."""

    def __init__(self, client):
        self.client = client
        self.enabled = True

        # 'seen events' won't trigger an immediate send.
        self._seen_events = None # defaultdict(set)

        # pending to be sent to server
        self._pending = defaultdict(list)
        self._new_events = defaultdict(dict)

        self._counter = 0
        self._urgent_event_seen = False
        self.pending_events = defaultdict(lambda: defaultdict(list))
        self._last_event_sent = datetime.now()
        self.mode = DISCOVERY_MODE
        self._initialize_seen_events()
        self._acum_len_data = 0

        self.load_events_data_from_server()

    @classmethod
    def init(cls, client):
        sec_ext = cls(client)
        return sec_ext

    def __repr__(self):
        # type: () -> Text
        return "SecurityExtensions(enabled=%r)" % self.enabled

    def _reset_pending(self):
        """After constants.<pending> all data related of how many times a """
        # pending to be sent to server
        self._last_event_sent = datetime.now()

        # keeps all data for new events
        self._new_events = defaultdict(dict)

        self._pending = defaultdict(list)
        self._urgent_event_seen = False

        # store new pending events
        if self.pending_events:
            for kind, event_hash in self.pending_events.items():
                self.store_seen_events_to_disk(kind, event_hash)

        # and now we can reset all pending events
        self.pending_events = defaultdict(lambda: defaultdict(list))
        self._counter = 0


    def _initialize_seen_events(self):
        self._seen_events = defaultdict(set)

    def get_named_tuple(self, kind):
        # TODO: refactor
        if kind == Proc.kind:
            return Proc().get_data_model()
        elif kind == Netstat.kind:
            return Netstat().get_data_model()

    def _get_commands_enabled(self):
        commands = [
            Proc(),
            Netstat()
        ]

        return commands

    def _get_timestamp(selfo):
        dt_now = datetime.now(tz=timezone.utc)
        return int(dt_now.timestamp())

    def _get_since_last_event_sent(self):
        dt = datetime.now() - self._last_event_sent
        return dt.seconds

    def _need_to_send_detected_events(self):
        return self._counter > constants.IDS_MAX_EVENTS \
            or self._get_since_last_event_sent() > constants.IDS_EVENT_PUSH_TIMEOUT \
            or (self._urgent_event_seen and self._get_since_last_event_sent() > constants.IDS_URGENT_EVENT_PUSH_TIMEOUT)


    def poll(self):
        # In case an event has been seen for the first time,
        # we send data earlier (but not inmediately, otherwise
        # it could be too verbose).

        commands = self._get_commands_enabled()

        self._counter += 1

        for cmd in commands:

            # all events from the same command will share the same timestamp
            timestamp = self._get_timestamp()

            # an event is a certain process, connection, etc.
            events = cmd.execute()

            for event in events:
                event_hash = cmd.get_hash_signature(event)

                if event_hash in self._seen_events[cmd.kind]:
                    # if there's an event that has been seen for
                    # the first time, we would push data earlier
                    # depending on IDS_URGENT_EVENT_PUSH_TIMEOUT
                    # instead of IDS_EVENT_PUSH_TIMEOUT.
                    self._urgent_event_seen = True

                else:
                    # add it temporarily to _event_data; in the next
                    # iteration of pushing data it will be sent.
                    self._new_events[cmd.kind][event_hash] = event
                    self._seen_events[cmd.kind].add(event_hash)
                self.pending_events[cmd.kind][event_hash].append(timestamp)

        if self._need_to_send_detected_events():
            for cmd in commands:
                self.send_pending_events(cmd.kind)
            self._reset_pending()

    def store_seen_events_to_disk(self, event_kind, seen_events, file_path=None):
        if not file_path:
            file_path = constants.IDS_EVENTS_PATH + constants.IDS_EVENTS_FILENAME

        with open("%s.%s" % (file_path, event_kind), 'a+') as f:
            # move the file pointer to the start of the file
            f.seek(0)

            # read the current hashes found in file
            # and append new hashes
            stored_event_hashes = f.read().splitlines()

            # write only events not found before
            for event_hash in seen_events:
                if event_hash not in stored_event_hashes:
                    f.write(str(event_hash) + '\n')

    def load_events(self):
        for cmd in self._get_commands_enabled():
            try:
                self.load_seen_events_from_disk(event_kind=cmd.kind)
            except:
                log.warning("Error loading event %s from disk", cmd.kind)

        self.load_events_data_from_server()

    def load_seen_events_from_disk(self, event_kind, file_path=None):
        if not file_path:
            file_path = constants.IDS_EVENTS_PATH + constants.IDS_EVENTS_FILENAME

        with open("%s.%s" % (file_path, event_kind), 'r') as f:
            stored_event_hashes = f.read().splitlines()
            for event_hash in stored_event_hashes:
                self._seen_events[event_kind].add(event_hash)

    def load_events_data_from_server(self):
        # type: () -> None

        log.debug("Starting initial load IDS data")
        headers = {
            "DA_TOKEN": f"{self.client.device_token}",
            'Content-Type': 'application/json'
        }

        response = contrib.requests_get_json(
            urljoin(self.client.rpc_url, "/events/anomalous/"),
            headers=headers
        )

        ids_data = response.data

        if not ids_data:
            log.warning("No ids loaded.")
            return
        elif not response.ok:
            log.warning("Error loading ids: %s / %s", response.data)
            return

        for kind, data_hash in ids_data.items():
            self._seen_events[kind].update(
                *data_hash
                )
            log.warning("Loaded %s items for %s (%s bytes)", len(data_hash), kind, len(str(data_hash)))

    def _get_pending_events(self, kind):
        events = self.pending_events[kind]
        result = []
        for event_hash, timestamps in events.items():
            _filtered_timestamps = self._filter_events_min_interval(timestamps, constants.IDS_MIN_EVENT_INTERVAL)
            _data = {
                event_hash: self._delta_timestamp(_filtered_timestamps)
            }
            result.append(dict(_data))
        return result

    def _get_new_events(self, kind):
        event_data = self._new_events[kind]
        result = []
        for event_hash, event in event_data.items():
            data = event._asdict()
            data["hash"] = event_hash
            result.append(data)
        return result
    def _delta_timestamp(self, timestamp_serie):
        deltas = [j - i for i, j in zip(timestamp_serie[:-1], timestamp_serie[1:])]
        # insert the first element at the beginning
        deltas.insert(0, timestamp_serie[0])
        return deltas

    def _filter_events_min_interval(self, events, min_interval=constants.IDS_MIN_EVENT_INTERVAL):
        result = []
        last_accepted = None

        for event in events:
            if last_accepted is None or event - last_accepted >= min_interval:
                result.append(event)
                last_accepted = event
        return result

    @tenacity.retry(
        wait=tenacity.wait_fixed(int(constants.IDS_RETRY_WAIT_SECONDS)),
        #retry=tenacity.retry_if_exception_type(pika.exceptions.AMQPConnectionError),
        stop=tenacity.stop_after_attempt(int(constants.IDS_RETRY_MAX_ATTEMPTS)),
        before_sleep=tenacity.before_sleep_log(log, logging.DEBUG)
    )
    def send_pending_events(self, kind):
        data = self._get_pending_events(kind)
        if not data:
            log.warning("Skipping sending pending events (no new events)")
            return

        json_data = {
            "payload": {
                "kind": kind,
                "data": data,
                "new_events": self._get_new_events(kind),
            }
        }

        headers = {
            "DA_TOKEN": f"{self.client.device_token}",
            'Content-Type': 'application/json'
        }
        len_data = len(str(json_data))
        self._acum_len_data += len_data
        log.warning("Sending %s bytes to IDS (%.2f KBs in total)",
                    len_data, self._acum_len_data/1024)

        response = contrib.requests_post_json(
            urljoin(self.client.rpc_url, "/events/"),
            data=json_data,
            headers=headers,
            )
        log.debug("IDS: %s / \n response: %s", json_data, response)
