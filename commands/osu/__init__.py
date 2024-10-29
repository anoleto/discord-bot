from typing import List

available_commands: List[str] = [
    'setprofile'
    'profile'
    'recent'
]

from .setprofile import SetProfile
from .profile import Profile
from .score import Score

__all__ = [
    'SetProfile',
    'Profile',
    'Score',
    'available_commands'
]

# XXX: maybe later?
# XXX: gotta rewrite my whole recent, top, etc command again :sob: