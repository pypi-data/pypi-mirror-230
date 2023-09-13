""" Class for managing pictorus apps and any associated run settings """
import json
import os
from subprocess import Popen, run
from tempfile import TemporaryFile
import threading
import time
from concurrent.futures import ThreadPoolExecutor


import requests
from awscrt import mqtt
from awsiot import iotshadow

from . import __version__ as CURRENT_VERSION
from .version_manager import VersionManager
from .config import load_app_manifest, store_app_manifest, APP_ASSETS_DIR, Config
from .telemetry_manager import TelemetryManager
from .logging import get_logger
from .constants import CmdType, AppLogLevel, PICTORUS_SERVICE_NAME

logger = get_logger()
config = Config()


def download_file(file_path: str, url: str):
    """Download a file to specified path"""
    logger.info("Downloading url: %s to path: %s", url, file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with requests.get(url, stream=True) as req, open(file_path, "wb") as in_file:
        req.raise_for_status()
        for chunk in req.iter_content(chunk_size=8192):
            in_file.write(chunk)


def cmd_topic(subtopic: str):
    return f"cmd/pictorus/{config.client_id}/{subtopic}"


class AppManager:
    """Manager responsible for pictorus apps on this device"""

    APP_VERSION_SHADOW_PROP = "app_version"
    RUN_APP_SHADOW_PROP = "run_app"
    ERROR_LOG_SHADOW_PROP = "error_log"
    LOG_LEVEL_SHADOW_PROP = "log_level"

    CMD_REQUEST_SUBTOPIC = "req"
    RETAINED_CMD_SUBTOPIC = "ret"

    APP_PATH = os.path.join(APP_ASSETS_DIR, "pictorus_managed_app")
    ERROR_LOG_PATH = os.path.join(APP_ASSETS_DIR, "pictorus_errors.json")
    PARAMS_PATH = os.path.join(APP_ASSETS_DIR, "diagram_params.json")

    EMPTY_ERROR = {
        "err_type": None,
        "message": None,
    }

    NO_LOG_ERROR = {
        "err_type": "NoLogError",
        "message": "App crashed unexpectedly",
    }

    def __init__(self, mqtt_connection: mqtt.Connection):
        self._telemetry_manager = TelemetryManager(mqtt_connection)
        self._pictorus_app_process: Popen = None
        self._version_manager: VersionManager = None
        self._error_log = self.EMPTY_ERROR.copy()
        self._app_manifest = load_app_manifest()
        self._mqtt_connection = mqtt_connection
        self._shadow_client = iotshadow.IotShadowClient(self._mqtt_connection)
        self._last_reported_shadow_state = None
        self._app_log_level = AppLogLevel.INFO

        self._update_reported_shadow_state()

        self.complete = threading.Event()
        self._app_watcher_thread = threading.Thread(target=self._watch_app)
        self._app_watcher_thread.start()

    def set_version_mgr(self, version_mgr: VersionManager):
        self._version_manager = version_mgr

    @property
    def app_is_running(self) -> bool:
        """Return whether the app is currently running"""
        return bool(self._pictorus_app_process)

    def _watch_app(self):
        while not self.complete.is_set():
            # If an app process has started, communicate() to catch unexpected terminations.
            if self._pictorus_app_process:
                logger.info("AppManager watching for Pictorus App crashes...")

                # Reset Error shadow state for each new app run
                self._error_log = self.EMPTY_ERROR.copy()
                self._update_reported_shadow_state()

                # Blocks until the app process ends
                self._pictorus_app_process.wait()

                # If app manager knows about shutdown, everything's fine
                if not self.app_is_running:
                    logger.info("Detected normal termination of Pictorus App")
                    continue

                logger.error("Pictorus App unexpectedly crashed!")
                # Check for PictorusError json file and set the shadow state error log to that.
                if os.path.exists(self.ERROR_LOG_PATH):
                    logger.warning("Sending Pictorus error logs...")
                    with open(self.ERROR_LOG_PATH, "r", encoding="utf-8") as error_file:
                        self._error_log = json.load(error_file)

                    logger.warning("Error log: %s", self._error_log)
                    os.remove(self.ERROR_LOG_PATH)
                else:
                    # There should always be a log. If not, return a special error so we know.
                    logger.warning("No error logs!")
                    self._error_log = self.NO_LOG_ERROR.copy()

                # The app has crashed and we've gathered all info, stop the app and push
                # the shadow state
                self._stop_app()
                self._update_reported_shadow_state()

            # If no app is currently running, prevent tight loop
            time.sleep(0.1)

        # Exit once self.complete Event() is set
        logger.info("Closing App Watcher thread...")

    def __enter__(self):
        self._maybe_start_app()
        self._init_subscriptions()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.complete.set()
        self._stop_app()
        self._telemetry_manager.stop_listening()

        self._mqtt_connection.unsubscribe(cmd_topic(self.CMD_REQUEST_SUBTOPIC))
        self._mqtt_connection.unsubscribe(cmd_topic(self.RETAINED_CMD_SUBTOPIC))

        if self._app_watcher_thread:
            self._app_watcher_thread.join()

    def _update_reported_shadow_state(self):
        cached_version = self._version_manager.last_installed if self._version_manager else None
        shadow_state = {
            "connected": True,
            self.APP_VERSION_SHADOW_PROP: self._app_manifest,
            self.RUN_APP_SHADOW_PROP: config.run_app,
            self.ERROR_LOG_SHADOW_PROP: self._error_log,
            self.LOG_LEVEL_SHADOW_PROP: self._app_log_level.value,
            "version": CURRENT_VERSION,
            "cached_version": cached_version,
        }

        # Don't publish an update if nothing changed. Otherwise we can get in a bad state
        # where IoT backend continuously publishes deltas and we respond with the same reported state
        if self._last_reported_shadow_state == shadow_state:
            return

        request = iotshadow.UpdateShadowRequest(
            thing_name=config.client_id,
            state=iotshadow.ShadowState(
                reported=shadow_state,
            ),
        )
        self._shadow_client.publish_update_shadow(request, mqtt.QoS.AT_LEAST_ONCE)
        self._last_reported_shadow_state = shadow_state

    def _maybe_start_app(self):
        # Don't start if we're already running or not configured to run
        if not config.run_app or self._pictorus_app_process:
            return

        build_hash = self._app_manifest.get("build_hash")
        if build_hash and os.path.exists(self.APP_PATH):
            logger.info("Starting pictorus app")
            self._telemetry_manager.start_listening(build_hash)
            # Wait for telemetry manager to be in a good state, but continue if it takes too long
            # so we're able to communicate with device manager even if something goes wrong
            self._telemetry_manager.ready.wait(timeout=30)
            # Could potentially pipe app output back to the backend/user if we want to
            host, port = self._telemetry_manager.socket_data
            try:
                self._pictorus_app_process = Popen(
                    self.APP_PATH,
                    env={
                        "APP_PUBLISH_SOCKET": f"{host}:{port}",
                        "APP_RUN_PATH": APP_ASSETS_DIR,
                        "LOG_LEVEL": self._app_log_level.value,
                    },
                )
            except OSError:
                logger.error("Failed to start app", exc_info=True)
        else:
            logger.info("No pictorus apps installed")

    def _init_subscriptions(self):
        self._shadow_client.subscribe_to_shadow_delta_updated_events(
            request=iotshadow.ShadowDeltaUpdatedSubscriptionRequest(thing_name=config.client_id),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_shadow_delta_updated,
        )

        self._mqtt_connection.subscribe(
            cmd_topic(self.CMD_REQUEST_SUBTOPIC),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_cmd_request,
        )

        self._mqtt_connection.subscribe(
            cmd_topic(self.RETAINED_CMD_SUBTOPIC),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_retained_cmd,
        )

    def _control_app_running(self, run_app: bool):
        config.run_app = run_app

        if run_app:
            self._maybe_start_app()
        else:
            self._stop_app()

    def _stop_app(self):
        if self._pictorus_app_process:
            logger.info("Stopping pictorus app")
            app_handle = self._pictorus_app_process
            self._pictorus_app_process = None
            app_handle.terminate()
            app_handle.wait()

    def _restart_app(self):
        self._stop_app()
        self._maybe_start_app()

    def _update_app(self, version_data: dict):
        build_hash = version_data.get("build_hash")
        app_bin_url = version_data.get("app_bin_url")
        params_hash = version_data.get("params_hash")
        params_url = version_data.get("params_url")
        if not build_hash or not app_bin_url or not params_hash or not params_url:
            logger.error("Invalid app update request: %s", version_data)
            return

        download_paths = []
        if self._app_manifest.get("build_hash") != build_hash:
            logger.info("Updating binary")
            download_paths.append((self.APP_PATH, app_bin_url))

        if self._app_manifest.get("params_hash") != params_hash:
            logger.info("Updating params")
            download_paths.append((self.PARAMS_PATH, params_url))

        if download_paths:
            self._stop_app()
            with ThreadPoolExecutor(max_workers=len(download_paths)) as executor:
                futures = [
                    executor.submit(download_file, path, url) for path, url in download_paths
                ]

            try:
                for fut in futures:
                    fut.result()
            except requests.exceptions.HTTPError:
                logger.error("Failed to update app", exc_info=True)
            else:
                os.chmod(self.APP_PATH, 0o755)
                self._app_manifest = {
                    "build_hash": build_hash,
                    "params_hash": params_hash,
                }
                store_app_manifest(self._app_manifest)
                logger.info("Successfully updated app")

        self._maybe_start_app()

    def _set_log_level(self, log_level: str):
        try:
            log_level = AppLogLevel(log_level)
        except ValueError:
            logger.warning("Received invalid log level: %s", log_level)
            return

        self._app_log_level = log_level
        self._restart_app()

    def _upload_logs(self, upload_config: dict):
        upload_data = upload_config["upload_dest"]
        line_count = str(upload_config["line_count"])

        with TemporaryFile("rb+") as tmp_log:
            run(
                ["journalctl", "-u", PICTORUS_SERVICE_NAME, "-n", line_count, "--no-pager"],
                check=True,
                stdout=tmp_log,
            )
            tmp_log.flush()
            tmp_log.seek(0)

            # TODO: This loads the entire uncompressed log contents into memory.
            # Would be nicer to write to a (possible compressed?) file and then upload in chunks
            # if data exceeds a certain size
            response = requests.post(
                upload_data["url"], data=upload_data["fields"], files={"file": tmp_log}
            )
            response.raise_for_status()

    def _process_cmd(self, payload: str):
        data = json.loads(payload)
        if "type" not in data or "data" not in data:
            logger.warning("Received invalid command: %s", data)
            return

        try:
            cmd_type = CmdType(data["type"])
        except ValueError:
            logger.warning("Unknown command type: %s", data["type"])
            return

        cmd_data = data["data"]

        if cmd_type == CmdType.UPDATE_APP:
            self._update_app(cmd_data)
        elif cmd_type == CmdType.SET_TELEMETRY_TLL:
            self._telemetry_manager.set_ttl(cmd_data["ttl_s"])
        elif cmd_type == CmdType.SET_LOG_LEVEL:
            self._set_log_level(cmd_data["log_level"])
        elif cmd_type == CmdType.UPLOAD_LOGS:
            self._upload_logs(cmd_data)
        else:
            logger.error("Unhandled command: %s", cmd_type)
            return

    def _on_retained_cmd(self, topic: str, payload: bytes):
        # This is an echo of the message we published to clear the retained message
        if not payload:
            return

        try:
            self._on_cmd_request(topic, payload)
        finally:
            # This is a retained message so clear it by publishing an empty payload
            # This is a barebones implementation for being able to queue actions for a device.
            # Right now it only allows a single queued command.
            # Eventually we can implement the full jobs API for more robust control of actions
            self._mqtt_connection.publish(
                topic=topic,
                payload="",
                qos=mqtt.QoS.AT_LEAST_ONCE,
                retain=True,
            )

    def _on_cmd_request(self, topic: str, payload: bytes):
        logger.debug("Received message on topic %s: %s", topic, payload)
        try:
            self._process_cmd(payload)
        finally:
            self._update_reported_shadow_state()

    def _on_shadow_delta_updated(self, delta: iotshadow.ShadowDeltaUpdatedEvent):
        if not delta.state:
            return

        if self.RUN_APP_SHADOW_PROP in delta.state:
            run_app = delta.state[self.RUN_APP_SHADOW_PROP]
            config.run_app = run_app

            if run_app:
                self._maybe_start_app()
            else:
                self._stop_app()

        self._update_reported_shadow_state()
