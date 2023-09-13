from typing import List, Optional

from aws_network_firewall.destination import Destination
from aws_network_firewall.engines.abstract import EngineAbstract
from aws_network_firewall.suricata import SuricataRule, SuricataHost, SuricataOption
from aws_network_firewall.suricata.host import Host


class TlsRule(EngineAbstract):
    def parse(self, destination: Destination) -> List[SuricataRule]:
        rules = []

        if not destination.tls_versions:
            rules = self.__resolve_rules(destination)

        if destination.tls_versions:
            rules = self.__resolve_tls_version_rules(destination)

        if destination.port != 443:
            rules.append(self.__resolve_tls_handshake(destination=destination))

        return rules

    def __resolve_rules(self, destination) -> List[SuricataRule]:
        return [
            SuricataRule(
                action="pass",
                protocol=destination.protocol,
                sources=self.suricata_source,
                destination=SuricataHost(
                    address=destination.cidr if destination.cidr else "",
                    port=destination.port if destination.port else 0,
                ),
                options=self.__resolve_tls_options(
                    destination=destination, ssl_version=None
                )
                + self.resolve_options(destination=destination),
            )
        ]

    @classmethod
    def __resolve_tls_options(
        cls, destination: Destination, ssl_version: Optional[str]
    ) -> List[SuricataOption]:
        options = [
            SuricataOption(name="tls.sni"),
        ]
        if ssl_version:
            options.append(
                SuricataOption(
                    name="ssl_version", value=ssl_version, quoted_value=False
                )
            )

        if destination.endpoint:
            options += cls.__resolve_sni_options(destination.endpoint)

        return options

    @staticmethod
    def __resolve_sni_options(endpoint: str) -> List[SuricataOption]:
        if endpoint.startswith("*"):
            return [
                SuricataOption(name="dotprefix"),
                SuricataOption(name="content", value=endpoint[1:]),
                SuricataOption(name="nocase"),
                SuricataOption(name="endswith"),
            ]

        return [
            SuricataOption(name="content", value=endpoint),
            SuricataOption(name="nocase"),
            SuricataOption(name="startswith"),
            SuricataOption(name="endswith"),
        ]

    def __resolve_tls_version_rules(
        self, destination: Destination
    ) -> List[SuricataRule]:
        ssl_version = ",".join(destination.tls_versions)

        return [
            SuricataRule(
                action="pass",
                protocol=destination.protocol,
                sources=self.suricata_source,
                destination=SuricataHost(
                    address=destination.cidr if destination.cidr else "",
                    port=destination.port if destination.port else 0,
                ),
                options=self.__resolve_tls_options(
                    destination=destination, ssl_version=ssl_version
                )
                + self.resolve_options(destination=destination),
            )
        ]

    def __resolve_tls_handshake(self, destination: Destination) -> SuricataRule:
        if not destination.message:
            destination.message = "Pass non-established TCP for 3-way handshake"
        else:
            destination.message += " | Pass non-established TCP for 3-way handshake"

        rule = SuricataRule(
            action="pass",
            protocol="TCP",
            sources=self.suricata_source,
            destination=SuricataHost(
                address=destination.cidr if destination.cidr else "",
                port=destination.port if destination.port else 0,
            ),
            options=[
                SuricataOption(name="flow", value="not_established", quoted_value=False)
            ]
            + self.resolve_options(destination),
        )
        rule.enable_bidirectional_communication()

        return rule
