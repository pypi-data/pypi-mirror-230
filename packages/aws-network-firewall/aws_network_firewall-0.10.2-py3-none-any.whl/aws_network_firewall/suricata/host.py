from __future__ import annotations

from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class Host:
    """
    Understands a source and/or destination defenition
    """

    address: str
    port: int

    def __post_init__(self):
        self.port = "any" if not self.port else self.port
        self.address = "any" if not self.address else self.address

    def __str__(self):
        return f"{self.address} {self.port}"
