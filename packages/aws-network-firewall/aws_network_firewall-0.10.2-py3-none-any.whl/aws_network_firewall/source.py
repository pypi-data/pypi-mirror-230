from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    """
    Understands a source
    """

    description: str
    cidr: Optional[str]
