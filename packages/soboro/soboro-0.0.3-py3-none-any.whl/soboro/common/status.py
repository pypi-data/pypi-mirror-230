# pyright: reportShadowedImports=false
from enum import Enum

__all__ = ["MonitorStatus"]


class MonitorStatus(str, Enum):
    unknown: str = "unknown"
    warned: str = "warned"
    warning: str = "warning"
    checking: str = "checking"
