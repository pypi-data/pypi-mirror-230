from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass
from aws_network_firewall.cidr_range import CidrRange


@dataclass
class CidrRanges:
    cidr_ranges: List[CidrRange]

    def by_region(self, region: str) -> Optional[CidrRange]:
        return next(filter(lambda cidr: cidr.region == region, self.cidr_ranges), None)  # type: ignore
