from typing import List

from aws_network_firewall.destination import Destination
from aws_network_firewall.engines.abstract import EngineAbstract
from aws_network_firewall.suricata import SuricataRule, SuricataHost
from aws_network_firewall.suricata.host import Host


class DnsRule(EngineAbstract):
    def parse(self, destination: Destination) -> List[SuricataRule]:
        def create_rule(protocol: str) -> SuricataRule:
            rule = SuricataRule(
                action="pass",
                protocol=protocol,
                sources=self.suricata_source,
                destination=SuricataHost(
                    address=destination.cidr if destination.cidr else "",
                    port=destination.port if destination.port else 53,
                ),
                options=self.resolve_options(destination=destination),
            )
            rule.enable_bidirectional_communication()
            return rule

        return [
            create_rule(protocol="TCP"),
            create_rule(protocol="UDP"),
        ]
