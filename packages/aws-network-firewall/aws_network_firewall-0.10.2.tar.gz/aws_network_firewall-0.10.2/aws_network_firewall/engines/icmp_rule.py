from typing import List

from aws_network_firewall.destination import Destination
from aws_network_firewall.engines.abstract import EngineAbstract
from aws_network_firewall.suricata import SuricataRule, SuricataHost
from aws_network_firewall.suricata.host import Host


class IcmpRule(EngineAbstract):
    def parse(self, destination: Destination) -> List[SuricataRule]:
        return [
            SuricataRule(
                action="pass",
                protocol=destination.protocol,
                sources=self.suricata_source,
                destination=SuricataHost(
                    address=destination.cidr if destination.cidr else "",
                    port=destination.port if destination.port else 0,
                ),
                options=self.resolve_options(destination),
            )
        ]
