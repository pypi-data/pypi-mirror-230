from pictorus.config import Config, APP_ASSETS_DIR

from unittest import TestCase
from unittest.mock import patch, mock_open, Mock, ANY
from typing import Callable
import threading
import time
import json

from awsiot.iotshadow import ShadowDeltaUpdatedEvent
import responses

from pictorus.app_manager import AppManager
from pictorus.constants import CmdType, AppLogLevel

config = Config()

ADDR_DATA = ("127.0.0.1", 1234)


def wait_for_condition(condition: Callable[[], bool], timeout=1):
    start = time.time()
    while not condition():
        if time.time() - start > timeout:
            raise TimeoutError()

        time.sleep(0.1)


def assert_correct_app_start(m_popen, log_level=AppLogLevel.INFO):
    m_popen.assert_called_once_with(
        AppManager.APP_PATH,
        env={
            "APP_PUBLISH_SOCKET": f"{ADDR_DATA[0]}:{ADDR_DATA[1]}",
            "APP_RUN_PATH": APP_ASSETS_DIR,
            "LOG_LEVEL": log_level.value,
        },
    )


@patch("pictorus.app_manager.Popen")
@patch("pictorus.app_manager.TelemetryManager")
class TestAppManager(TestCase):
    BUILD_ID = "bob"

    def setUp(self):
        # Don't want this to actually overwrite config
        write_patch = patch("pictorus.config.Config._write_config")
        write_patch.start()
        self.addCleanup(write_patch.stop)

        config.store_config({"clientId": "foo_device"})

        app_manifest_patch = patch(
            "pictorus.app_manager.load_app_manifest",
            return_value={"build_hash": self.BUILD_ID, "params_hash": "bar"},
        )
        app_manifest_patch.start()
        self.addCleanup(app_manifest_patch.stop)

        shadow_patch = patch("pictorus.app_manager.iotshadow.IotShadowClient")
        shadow_patch.start()
        self.addCleanup(shadow_patch.stop)

        exists_patch = patch("pictorus.app_manager.os.path.exists", return_value=True)
        self.m_exists = exists_patch.start()
        self.addCleanup(exists_patch.stop)

    def test_starts_app_on_entry(self, m_telem, m_popen):
        m_telem.return_value.socket_data = ADDR_DATA
        config.run_app = True

        with AppManager(Mock()):
            m_telem.return_value.start_listening.assert_called_once_with(self.BUILD_ID)
            assert_correct_app_start(m_popen)

        m_popen.return_value.terminate.assert_called_once()

    def test_does_not_start_app_on_entry(self, m_telem, m_popen):
        config.run_app = False
        with AppManager(Mock()):
            m_telem.return_value.start_listening.assert_not_called()
            m_popen.assert_not_called()

        m_popen.return_value.terminate.assert_not_called()

    def test_starts_and_stops_app_based_on_shadow(self, m_telem, m_popen):
        m_telem.return_value.socket_data = ADDR_DATA
        with AppManager(Mock()) as mgr:
            # Start the app
            mgr._on_shadow_delta_updated(ShadowDeltaUpdatedEvent(state={"run_app": True}))
            m_telem.return_value.start_listening.assert_called_once_with(self.BUILD_ID)
            assert_correct_app_start(m_popen)
            assert config.run_app is True

            # Should not restart if already running
            m_telem.reset_mock()
            m_popen.reset_mock()
            mgr._on_shadow_delta_updated(ShadowDeltaUpdatedEvent(state={"run_app": True}))
            m_telem.return_value.start_listening.assert_not_called()
            m_popen.assert_not_called()
            assert config.run_app is True

            # Stop the app
            mgr._on_shadow_delta_updated(ShadowDeltaUpdatedEvent(state={"run_app": False}))
            m_popen.return_value.terminate.assert_called_once()
            assert config.run_app is False

    @responses.activate
    @patch("pictorus.app_manager.os.makedirs")
    @patch("pictorus.app_manager.os.chmod")
    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_starts_app_on_update(self, m_shadow_req, _, __, m_telem, m_popen):
        m_telem.return_value.socket_data = ADDR_DATA
        config.run_app = True
        new_build_id = "newfoo"
        new_params_hash = "newparams123"
        version_url = "http://foo.bar/baz"
        params_url = "http://foo.bar/params.json"

        responses.add(responses.GET, version_url, body="")
        responses.add(responses.GET, params_url, body="")

        m_write = mock_open()
        version_data = {
            "build_hash": new_build_id,
            "app_bin_url": version_url,
            "params_hash": new_params_hash,
            "params_url": params_url,
        }

        manifest_data = {"build_hash": new_build_id, "params_hash": new_params_hash}
        update_app_cmd = json.dumps({"type": CmdType.UPDATE_APP.value, "data": version_data})
        with AppManager(Mock()) as mgr, patch("builtins.open", m_write):
            m_telem.reset_mock()
            m_popen.reset_mock()

            mgr._on_cmd_request("req", update_app_cmd)
            m_telem.return_value.start_listening.assert_called_once_with(new_build_id)
            assert_correct_app_start(m_popen)
            assert config.run_app is True

            handle = m_write()
            handle.write.assert_called_once_with(json.dumps(manifest_data))

        assert m_shadow_req.mock_calls[1][2]["state"].reported["app_version"] == manifest_data

    def test_set_telemetry_ttl(self, m_telem, _):
        ttl_s = 99
        set_ttl_cmd = json.dumps(
            {"type": CmdType.SET_TELEMETRY_TLL.value, "data": {"ttl_s": ttl_s}}
        )
        with AppManager(Mock()) as mgr:
            mgr._on_cmd_request("req", set_ttl_cmd)
            m_telem.return_value.set_ttl.assert_called_once_with(ttl_s)

    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_set_log_level(self, m_shadow_req, m_telem, m_popen):
        m_telem.return_value.socket_data = ADDR_DATA
        config.run_app = True
        log_level = AppLogLevel.DEBUG
        set_ttl_cmd = json.dumps(
            {"type": CmdType.SET_LOG_LEVEL.value, "data": {"log_level": log_level.value}}
        )
        with AppManager(Mock()) as mgr:
            m_popen.reset_mock()
            mgr._on_cmd_request("req", set_ttl_cmd)
            assert_correct_app_start(m_popen, log_level=log_level)

        assert m_shadow_req.mock_calls[1][2]["state"].reported["log_level"] == log_level.value

    @responses.activate
    @patch("pictorus.app_manager.run")
    def test_set_upload_logs(self, m_run, _, __):
        upload_url = "https://example.com/upload"

        upload_logs_cmd = json.dumps(
            {
                "type": CmdType.UPLOAD_LOGS.value,
                "data": {
                    "upload_dest": {"url": upload_url, "fields": {"foo": "bar"}},
                    "line_count": 500,
                },
            }
        )
        responses.add(responses.POST, upload_url, body="")
        m_mqtt = Mock()
        with AppManager(m_mqtt) as mgr:
            mgr._on_retained_cmd("ret", upload_logs_cmd)
            m_run.assert_called_once_with(
                ["journalctl", "-u", "pictorus", "-n", "500", "--no-pager"],
                check=True,
                stdout=ANY,
            )
            m_mqtt.publish.assert_called_once_with(
                topic="ret",
                payload="",
                qos=ANY,
                retain=True,
            )

    @patch("pictorus.app_manager.os.remove")
    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_sets_error_from_file_on_unexpected_crash(
        self, m_shadow_req, m_remove, m_telem, m_popen
    ):
        m_telem.return_value.socket_data = ADDR_DATA
        app_complete = threading.Event()
        m_popen.return_value.wait.return_value = app_complete
        config.run_app = True

        expected_err = {"err_type": "Foo", "message": "Bar"}

        with AppManager(Mock()) as mgr, patch(
            "builtins.open", mock_open(read_data=json.dumps(expected_err))
        ):
            # Error should get cleared on init
            assert (
                m_shadow_req.call_args[1]["state"].reported["error_log"] == AppManager.EMPTY_ERROR
            )
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_called_once_with(AppManager.ERROR_LOG_PATH)
        assert m_shadow_req.call_args[1]["state"].reported["error_log"] == expected_err

    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_sets_default_error_on_unexpected_crash(self, m_shadow_req, m_telem, m_popen):
        m_telem.return_value.socket_data = ADDR_DATA
        app_complete = threading.Event()
        m_popen.return_value.wait.return_value = app_complete
        self.m_exists.side_effect = lambda p: p != AppManager.ERROR_LOG_PATH
        config.run_app = True

        with AppManager(Mock()) as mgr:
            # Error should get cleared on init
            assert (
                m_shadow_req.call_args[1]["state"].reported["error_log"] == AppManager.EMPTY_ERROR
            )
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        assert m_shadow_req.call_args[1]["state"].reported["error_log"] == AppManager.NO_LOG_ERROR
