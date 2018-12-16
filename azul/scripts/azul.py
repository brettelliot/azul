"""
    Note: when testing this do:
    $ pip install --editable .

    But if you make a change:
    $ pip uninstall azul
    $ pip install --editable .

    Also note, if you are in the top azul directory and type "azul" with no other options the shell will take you
    the azul directory instead of running the command line.
"""

import click
import azul
import logbook


@click.group()
def cli():
    """azul is a command line tool for downloading historical price data that can be used in a zipline bundle."""

    # install a logbook handler before performing any other operations
    logbook.StderrHandler().push_application()
    global log
    log = logbook.Logger('AzulCli')


@click.command()
@click.option(
    '--source',
    type=click.Choice({'sp500', 'polygon_cs', 'iex'}),
    default='sp500',
    show_default=True,
    help='The list of symbols from a specific source.',
)
@click.option(
    '-o',
    '--output',
    default=None,
    metavar='FILENAME',
    show_default=True,
    help="The directory or file to write the symbol list. The default directory is ~/.azul/symbols."
)
def symbols(source, output):
    """Get a list of symbols."""
    try:
        azul.write_symbols(source, output)
    except Exception as e:
        log.error(e)
        raise


@click.command()
def download():
    """Download historical price data."""
    pass


@click.command()
def update():
    """Update symbols with any new data."""
    pass


cli.add_command(symbols)
cli.add_command(download)
cli.add_command(update)
