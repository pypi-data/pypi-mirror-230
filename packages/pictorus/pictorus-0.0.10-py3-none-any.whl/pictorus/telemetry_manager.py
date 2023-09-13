from datetime import datetime, timezone, timedelta
import json
import os
import socket
import threading

from awscrt import mqtt

from pictorus.config import Config
from pictorus.logging import get_logger

logger = get_logger()
config = Config()

TELEM_HOST = "127.0.0.1"
UDP_BUFFER_SIZE_BYTES = 65507  # Max buffer for IPv4


def get_basic_ingest_topic(rule_name: str, topic: str):
    """Get the basic ingest topic for a given rule and base topic"""
    return os.path.join("$aws/rules/", rule_name, topic)


class TelemetryManager:
    """
    Class for managing telemetry from a running pictorus app.
    This class is responsible for communication between the app and device manager,
    as well as publishing telemetry to the backend at the correct interval
    """

    PUBLISH_INTERVAL_MS = 100

    def __init__(self, mqtt_connection: mqtt.Connection):
        self._listener_thread: threading.Thread = None
        self._build_id = ""
        self._message_topic = get_basic_ingest_topic(
            "app_telemetry_test",
            f"dt/pictorus/{config.client_id}/telem",
        )
        self._mqtt_connection = mqtt_connection
        self._listen = True
        self._last_publish_time = datetime.min
        self._ttl_dt = datetime.min
        # TODO: This should come from config
        self._publish_interval = timedelta(milliseconds=self.PUBLISH_INTERVAL_MS)
        self.socket_data = None
        self.ready = threading.Event()

    def set_ttl(self, ttl_s: int):
        """Set the telemetry TTL"""
        self._ttl_dt = datetime.utcnow() + timedelta(seconds=ttl_s)
        logger.debug("Updated TTL to: %s (UTC)", self._ttl_dt)

    def start_listening(self, build_id: str):
        """Start listening to the specified app"""
        self._build_id = build_id
        self._listen = True
        if not self._listener_thread:
            logger.info("Starting new listener thread...")
            self._listener_thread = threading.Thread(target=self.listen)
            self._listener_thread.start()
        else:
            logger.info("Listener already active!")

    def listen(self):
        """Main function for listening to app telem"""
        # Create UDP socket
        logger.info("Listening...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to any available port
            sock.bind((TELEM_HOST, 0))

            self.socket_data = sock.getsockname()
            self.ready.set()
            while self._listen:
                try:
                    data = sock.recv(UDP_BUFFER_SIZE_BYTES)
                    # Maybe this should come from the received data?
                    data_time_utc = datetime.utcnow()
                    ttl_active = data_time_utc < self._ttl_dt
                    # Currently this just throws away data unless we're publishing.
                    # Possible we might want to batch and upload everything in the future.
                    if (
                        ttl_active
                        and data_time_utc - self._last_publish_time >= self._publish_interval
                    ):
                        self._publish_app_telem(json.loads(data), data_time_utc)
                        self._last_publish_time = data_time_utc

                except json.JSONDecodeError:
                    logger.warning("Failed to read socket data", exc_info=True)

        self.socket_data = None

    def stop_listening(self):
        """Stop listening to all apps"""
        logger.info("Stopping listening...")
        self._listen = False
        if self._listener_thread:
            self._listener_thread.join()
        logger.info("Stopped listening...")

    def _publish_app_telem(self, app_data: dict, data_time_utc: datetime):
        publish_data = {
            "data": app_data,
            "time_utc": int(round(data_time_utc.replace(tzinfo=timezone.utc).timestamp() * 1000)),
            "meta": {"build_id": self._build_id},
        }
        logger.debug("Publishing most recent app data: %s", publish_data)
        self._mqtt_connection.publish(
            topic=self._message_topic,
            payload=json.dumps(publish_data),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
