from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CidrRange:
    """
    Understands a CidrRange
    """

    region: str
    value: str
