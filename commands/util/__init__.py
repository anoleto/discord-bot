from typing import List

available_commands: List[str] = [
    'ping',
    'uptime'
]

from .ping import Ping
from .uptime import Uptime

__all__ = [
    'Ping',
    'Uptime',
    'available_commands'
]