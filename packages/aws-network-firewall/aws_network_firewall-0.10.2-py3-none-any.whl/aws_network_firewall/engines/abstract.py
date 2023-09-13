from typing import List, Any, Optional
from abc import (
    ABC,
    abstractmethod,
)

from aws_network_firewall.destination import Destination
from aws_network_firewall.sid_state import SidState
from aws_network_firewall.suricata import SuricataRule, SuricataOption
from aws_network_firewall.suricata.host import Host


class EngineAbstract(ABC):
    __options: Optional[List[SuricataOption]]

    def __init__(self, rule: Any, sid_state: Optional[SidState]) -> None:
        self.__rule = rule
        self.__sid_state = sid_state

    @property
    def suricata_source(self) -> List[Host]:
        return self.__rule.suricata_source

    @abstractmethod
    def parse(self, destination: Destination) -> List[SuricataRule]:
        raise NotImplementedError

    def resolve_sid(self) -> int:
        if not self.__sid_state:
            return 0

        return self.__sid_state.allocate_sid(
            rule_type=self.__rule.type, region=self.__rule.region
        )

    def resolve_options(self, destination: Destination) -> List[SuricataOption]:
        message = (
            f"{destination.message} | {self.__rule.workload} | {self.__rule.name}"
            if destination.message
            else f"{self.__rule.workload} | {self.__rule.name}"
        )

        return [
            SuricataOption(name="msg", value=message),
            SuricataOption(
                name="sid", value=str(self.resolve_sid()), quoted_value=False
            ),
            SuricataOption(name="rev", value="1", quoted_value=False),
        ]
