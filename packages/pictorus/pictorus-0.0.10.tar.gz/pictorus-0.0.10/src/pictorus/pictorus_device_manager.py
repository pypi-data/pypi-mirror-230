#!/usr/bin/env python3

""" Daemon process for handling IoT interactions """
import json
import sys
import time
import os

from awsiot import mqtt_connection_builder
from awscrt import mqtt
from awscrt.exceptions import AwsCrtError

from pictorus.config import Config
from pictorus.logging import get_logger
from pictorus.app_manager import AppManager
from pictorus.version_manager import VersionManager

logger = get_logger()
config = Config()

CONNECT_RETRY_TIMEOUT_S = 15


def create_mqtt_connection():
    """Connect to the MQTT broker"""
    # AWS does not update device shadows from LWT messages, so we need to publish
    # to a standard topic and then republish on the backend:
    # https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-comms-app.html#thing-connection
    lwt = mqtt.Will(
        topic=f"my/things/{config.client_id}/shadow/update",
        qos=1,
        payload=json.dumps({"state": {"reported": {"connected": False}}}).encode(),
        retain=False,
    )
    mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
        client_id=config.client_id,
        endpoint=config.mqtt_endpoint,
        cert_bytes=config.credentials["certificatePem"].encode(),
        pri_key_bytes=config.credentials["keyPair"]["PrivateKey"].encode(),
        ca_bytes=config.credentials["certificateCa"].encode(),
        will=lwt,
        keep_alive_secs=120,
    )

    return mqtt_connection


def main():
    """Main run function"""
    log_level = os.environ.get(key="LOG_LEVEL", default="INFO").upper()
    logger.setLevel(log_level)
    logger.info("Starting device manager for device: %s", config.client_id)
    mqtt_connection = create_mqtt_connection()
    connect_future = mqtt_connection.connect()

    with AppManager(mqtt_connection) as app_mgr, VersionManager() as version_mgr:
        app_mgr.set_version_mgr(version_mgr)
        while True:
            try:
                connect_future.result()
                break
            except AwsCrtError:
                logger.warning(
                    "Connection failed. Retrying in: %ss", CONNECT_RETRY_TIMEOUT_S, exc_info=True
                )
                connect_future = mqtt_connection.connect()
                time.sleep(CONNECT_RETRY_TIMEOUT_S)

        logger.info("Connected to MQTT broker")
        app_mgr.complete.wait()


if __name__ == "__main__":
    sys.exit(main())
