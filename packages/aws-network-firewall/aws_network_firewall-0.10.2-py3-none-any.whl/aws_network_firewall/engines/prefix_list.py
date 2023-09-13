from typing import List

from aws_network_firewall.destination import Destination
from aws_network_firewall.engines.abstract import EngineAbstract
from aws_network_firewall.suricata import SuricataRule, SuricataHost


class PrefixList(EngineAbstract):
    def parse(self, destination: Destination) -> List[SuricataRule]:
        return [
            SuricataRule(
                action="pass",
                protocol=destination.protocol,
                sources=self.suricata_source,
                destination=SuricataHost(
                    address=destination.endpoint if destination.endpoint else "",
                    port=destination.port if destination.port else 0,
                ),
                options=self.resolve_options(destination),
            )
        ]
