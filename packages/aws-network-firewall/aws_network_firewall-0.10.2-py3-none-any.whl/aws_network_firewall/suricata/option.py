from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass
class Option:
    """
    Understands how to define options for a suricata rule
    """

    name: str
    value: Union[str, int, None] = None
    quoted_value: bool = True

    def __str__(self):
        value = self.value

        if self.quoted_value:
            value = f'"{self.value}"'

        return self.name if not self.value else f"{self.name}:{value}"
