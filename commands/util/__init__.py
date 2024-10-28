from typing import List

available_commands: List[str] = [
    'ping',
    'uptime',
    'eval'
]

from .ping import Ping
from .uptime import Uptime
from .eval import Eval

__all__ = [
    'Ping',
    'Uptime',
    'Eval',
    'available_commands'
]