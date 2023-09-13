from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, ClassVar, Dict


@dataclass
class Destination:
    """
    Understands a destination
    """

    description: str
    protocol: str
    port: Optional[int]
    endpoint: Optional[str]
    cidr: Optional[str]
    message: Optional[str]
    tls_versions: List[str]

    DEFAULT_RULE: ClassVar[str] = "DefaultRule"
    ICMP_RULE: ClassVar[str] = "IcmpRule"
    DNS_RULE: ClassVar[str] = "DnsRule"
    TLS_RULE: ClassVar[str] = "TlsRule"
    PREFIX_LIST: ClassVar[str] = "PrefixList"

    def __resolve_by_protocol(self, protocol: str) -> str:
        return {
            "ICMP": self.ICMP_RULE,
            "DNS": self.DNS_RULE,
            "TLS": self.TLS_RULE,
        }.get(protocol, self.DEFAULT_RULE)

    def __is_prefix_list(self) -> bool:
        return bool(
            self.protocol == "TCP" and self.endpoint and self.endpoint.startswith("@")
        )

    @property
    def type(self) -> str:
        if self.__is_prefix_list():
            return self.PREFIX_LIST

        return self.__resolve_by_protocol(self.protocol)
