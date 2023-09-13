from typing import Dict


class SidState:
    __state: Dict[str, Dict[str, int]]

    def __init__(self, sid_range: str) -> None:
        self.__state = {}
        self.__min = 0
        self.__max = 0

        if sid_range:
            minimum, maximum = sid_range.split("-")
            self.__min = int(minimum)
            self.__max = int(maximum)

    def __resolve_next_value(self, rule_type: str, region: str):
        has_type = self.__state.get(rule_type)

        if not has_type:
            self.__state[rule_type] = {}

        has_region = self.__state.get(rule_type, {}).get(region)

        if not has_region:
            self.__state[rule_type][region] = self.__min
        else:
            self.__state[rule_type][region] += 1

        return self.__state[rule_type][region]

    def allocate_sid(self, rule_type: str, region: str) -> int:
        if not self.__min:
            return 0

        return self.__resolve_next_value(rule_type=rule_type, region=region)
