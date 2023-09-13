from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import List, Optional, ClassVar

from aws_network_firewall.engines.dns_rule import DnsRule
from aws_network_firewall.engines.icmp_rule import IcmpRule
from aws_network_firewall.engines.prefix_list import PrefixList
from aws_network_firewall.engines.default_rule import DefaultRule
from aws_network_firewall.engines.tls_rule import TlsRule
from aws_network_firewall.sid_state import SidState
from aws_network_firewall.source import Source
from aws_network_firewall.destination import Destination
from aws_network_firewall.suricata import SuricataRule, SuricataHost


@dataclass
class Rule:
    """
    Understands a rule
    """

    workload: str
    name: str
    type: str
    region: str
    description: str
    sources: List[Source]
    destinations: List[Destination]

    INSPECTION: ClassVar[str] = "Inspection"
    EGRESS: ClassVar[str] = "Egress"

    __sid_state: Optional[SidState] = None

    def register_sid_state(self, sid_state: SidState) -> None:
        self.__sid_state = sid_state

    @property
    def is_inspection_rule(self) -> bool:
        return self.type == self.INSPECTION

    @property
    def is_egress_rule(self) -> bool:
        return self.type == self.EGRESS

    @property
    def suricata_source(self) -> List[SuricataHost]:
        def convert_source(source: Source) -> Optional[SuricataHost]:
            return SuricataHost(address=source.cidr, port=0) if source.cidr else None

        return list(filter(None, map(convert_source, self.sources)))

    def __resolve_rule(self, destination: Destination) -> List[SuricataRule]:
        pre_mapping = {
            Destination.ICMP_RULE: IcmpRule,
            Destination.TLS_RULE: TlsRule,
            Destination.DNS_RULE: DnsRule,
            Destination.PREFIX_LIST: PrefixList,
        }
        engine = pre_mapping.get(destination.type, DefaultRule)
        return engine(rule=self, sid_state=self.__sid_state).parse(  # type: ignore
            destination=destination
        )

    @property
    def suricata_rules(self) -> List[SuricataRule]:
        rules = list(filter(None, map(self.__resolve_rule, self.destinations)))
        return list(itertools.chain.from_iterable(rules))

    def __str__(self) -> str:
        return "\n".join(map(str, self.suricata_rules))
