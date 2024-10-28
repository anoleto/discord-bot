from typing import List

available_commands: List[str] = [
    'setprofile'
    'profile'
]

from .setprofile import SetProfile
from .profile import Profile

__all__ = [
    'SetProfile',
    'Profile',
    'available_commands'
]

# XXX: maybe later?
# XXX: gotta rewrite my whole recent, top, etc command again :sob: