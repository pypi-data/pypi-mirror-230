import click

from landingzone_organization.cli import Context
from landingzone_organization.workloads import Workloads

from aws_network_firewall.documentation_generator import DocumentationGenerator
from aws_network_firewall.schemas import environment_resolver


@click.group()
def cli() -> None:
    """
    Update command for example the docs
    """
    pass


@cli.command()  # type: ignore
@click.pass_obj
@click.argument("template_path")
@click.argument("config_path")
def docs(ctx: Context, template_path: str, config_path: str) -> None:
    """
    Render the firewall rules for the given path
    """
    ctx.info("Render firewall rules")
    ctx.debug(f"Path: {config_path}")
    ctx.debug(f"Template: {template_path}")

    workloads = Workloads.load_by_path(
        path=config_path, environment_resolver=environment_resolver
    )
    ctx.debug(f"\tdetected: {len(workloads.names)} workloads")
    ctx.debug(f"\tdetected: {len(workloads.accounts)} accounts")

    for workload in workloads:
        ctx.info(f"\tWorkload: {workload.name}")
        DocumentationGenerator(
            template_path=template_path, config_path=config_path, workload=workload
        ).render()
