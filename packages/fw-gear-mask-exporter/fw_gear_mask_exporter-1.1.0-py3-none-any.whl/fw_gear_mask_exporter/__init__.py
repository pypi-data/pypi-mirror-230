"""The fw_gear_task_exporter package."""
from importlib.metadata import version

try:
    __version__ = version(__package__)
except:  # pragma: no cover
    pass
