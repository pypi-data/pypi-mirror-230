from __future__ import annotations

from typing import List, Dict
from landingzone_organization import Account as LandingZoneAccount
from aws_network_firewall.cidr_ranges import CidrRanges
from aws_network_firewall.rule import Rule
from aws_network_firewall.rule_set import RuleSet
from aws_network_firewall.sid_state import SidState
from aws_network_firewall.source import Source


class Account(LandingZoneAccount):
    __rules: RuleSet
    __cidr_ranges: CidrRanges
    __sid_state: SidState

    def __init__(
        self,
        name: str,
        account_id: str,
        cidr_ranges: CidrRanges,
        sid_range: str,
        rules: List[Rule],
    ) -> None:
        super().__init__(name, account_id)

        self.__cidr_ranges = cidr_ranges
        self.__sid_state = SidState(sid_range=sid_range)
        self.__rules = RuleSet(rules=list(map(self.__enrich_rule, rules)))

    def __enrich_rule(self, rule: Rule) -> Rule:
        rule.register_sid_state(self.__sid_state)
        cidr_range = self.__cidr_ranges.by_region(rule.region)

        def update_cidr_if_not_set(entry: Source) -> None:
            if cidr_range and not entry.cidr:
                entry.cidr = cidr_range.value

        list(map(update_cidr_if_not_set, rule.sources))

        return rule

    @property
    def regions(self) -> List[str]:
        return list(set(filter(None, map(lambda rule: rule.region, self.rules.all))))

    def rules_by_region(self, region: str) -> RuleSet:
        return RuleSet(
            rules=list(filter(lambda rule: region == rule.region, self.rules.all))
        )

    @property
    def rules(self) -> RuleSet:
        return self.__rules

    @property
    def inspection_rules(self) -> List[Rule]:
        return list(filter(lambda rule: rule.is_inspection_rule, self.rules.all))

    @property
    def egress_rules(self) -> List[Rule]:
        return list(filter(lambda rule: rule.is_egress_rule, self.rules.all))
