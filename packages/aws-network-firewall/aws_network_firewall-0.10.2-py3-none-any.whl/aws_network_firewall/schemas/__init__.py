import os

from aws_network_firewall.account import Account
from landingzone_organization.schemas import load_schema, safe_load_file

from aws_network_firewall.cidr_ranges import CidrRanges, CidrRange
from aws_network_firewall.rule import Rule
from aws_network_firewall.destination import Destination
from aws_network_firewall.source import Source

schema_path = os.path.dirname(os.path.abspath(__file__))
EnvironmentSchema = load_schema(os.path.join(schema_path, "environment.yaml"))


def source_resolver(entry: dict) -> Source:
    return Source(
        description=entry["Description"],
        cidr=entry.get("Cidr"),
    )


def destination_resolver(entry: dict) -> Destination:
    return Destination(
        description=entry["Description"],
        protocol=entry["Protocol"],
        port=entry.get("Port"),
        endpoint=entry.get("Endpoint"),
        cidr=entry.get("Cidr"),
        message=entry.get("Message"),
        tls_versions=entry.get("TLSVersions", []),
    )


def rule_resolver(workload: str, entry: dict) -> Rule:
    return Rule(
        workload=workload,
        type=entry["Type"],
        region=entry["Region"],
        name=entry["Name"],
        description=entry["Description"],
        sources=list(map(source_resolver, entry["Sources"])),
        destinations=list(map(destination_resolver, entry["Destinations"])),
    )


def cidr_ranges_resolver(entry: dict) -> CidrRanges:
    ranges = []

    if entry:
        for region, cidr in entry.items():
            ranges.append(CidrRange(region=region, value=cidr))

    return CidrRanges(cidr_ranges=ranges)


def environment_resolver(path: str) -> Account:
    data = safe_load_file(EnvironmentSchema, path)

    def internal_resolver(entry: dict) -> Rule:
        return rule_resolver(workload=data["Name"], entry=entry)

    return Account(
        name=data["Name"],
        account_id=data["AccountId"],
        cidr_ranges=cidr_ranges_resolver(data.get("CidrRanges", {})),
        sid_range=data.get("SidRange", ""),
        rules=list(map(internal_resolver, data.get("Rules", []))),
    )
