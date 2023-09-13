""" Common constants and enums """
from enum import Enum

PICTORUS_SERVICE_NAME = "pictorus"


class CmdType(Enum):
    """Supported commands for the device command topic"""

    UPDATE_APP = "UPDATE_APP"
    SET_LOG_LEVEL = "SET_LOG_LEVEL"
    UPLOAD_LOGS = "UPLOAD_LOGS"
    SET_TELEMETRY_TLL = "SET_TELEMETRY_TTL"


class AppLogLevel(Enum):
    """Log levels that can be set for pictorus apps"""

    OFF = "off"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"
