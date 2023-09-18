"""Console script for sesr_tool."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for sesr_tool."""
    click.echo("Replace this message by putting your code into "
               "sesr_tool.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
