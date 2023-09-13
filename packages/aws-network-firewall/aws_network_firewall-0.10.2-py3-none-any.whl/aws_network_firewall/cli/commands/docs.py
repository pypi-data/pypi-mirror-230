import click
import jsonschema2md

from aws_network_firewall.schemas import EnvironmentSchema


@click.command()
def cli() -> None:
    parser = jsonschema2md.Parser(
        examples_as_yaml=True,
        show_examples="all",
    )
    md_lines = parser.parse_schema(EnvironmentSchema)

    with open("./docs/content/schema.md", "w") as fh:
        fh.writelines(md_lines)
