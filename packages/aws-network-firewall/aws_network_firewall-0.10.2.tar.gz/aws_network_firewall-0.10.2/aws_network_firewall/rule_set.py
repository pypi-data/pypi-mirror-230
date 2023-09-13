from __future__ import annotations

from typing import List

from aws_network_firewall.rule import Rule


class RuleSet:
    __rules: List[Rule]

    def __init__(self, rules: List[Rule]) -> None:
        self.__rules = rules

    def __len__(self) -> int:
        return len(self.all)

    def __iter__(self):
        for value in self.all:
            yield value

    @property
    def all(self) -> List[Rule]:
        return self.__rules

    @property
    def inspection_rules(self) -> List[Rule]:
        return list(filter(lambda rule: rule.is_inspection_rule, self.all))

    @property
    def egress_rules(self) -> List[Rule]:
        return list(filter(lambda rule: rule.is_egress_rule, self.all))
