from typing import List

available_commands: List[str] = [
    'wordbomb'
]

from .wordbomb import WordBomb

__all__ = [
    'WordBomb',
    'available_commands'
]