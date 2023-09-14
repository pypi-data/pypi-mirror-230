import traceback
import functools
import sys
import shutil

import click
from click_help_colors import HelpColorsGroup

from .sources import AirbyteSourceException
from .connections import Connection, list_connections



@click.group(
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='cyan'
)
def cli():
    pass


def print_color(msg):
    click.echo(click.style(msg, fg='cyan'))

def print_success(msg):
    click.echo(click.style(f'SUCCESS: {msg}', fg='green'))

def print_info(msg):
    click.echo(click.style(f'INFO: {msg}', fg='yellow'))

def print_command(msg):
    click.echo(click.style(f'INFO: `{msg}`', fg='magenta'))

def print_warning(msg):
    click.echo(click.style(f'WARNING: {msg}', fg='cyan'))


def handle_error(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (AssertionError, AirbyteSourceException) as e:
            click.echo(click.style(f'ERROR: {e}', fg='red'))
            sys.exit()
        except Exception as e:
            click.echo(click.style(f'ERROR: {e}', fg='red'))
            print(traceback.format_exc())
            sys.exit()

    return wrapper




@cli.command()
@click.argument('connection')
@click.option('--source', default='airbyte/source-faker:0.1.4', help='Any Public Docker Airbyte Source. Example: `airbyte/source-faker:0.1.4`. (see connectors list at: "https://hub.docker.com/search?q=airbyte%2Fsource-" )')
@click.option('--destination', default='print', help='One of `print` or `bigquery`')
@handle_error
def create(connection, source, destination):
    '''
    Create CONNECTION
    '''
    connection = Connection(connection)
    connection.init(source, destination)
    print_success(f'Created connection `{connection.name}` with source `{source}` and destination `{destination}`')


@cli.command()
@handle_error
def list():
    '''
    List created connections
    '''
    print_success(
        'Configured Connections are:\n' +
        '\n'.join([f'- {connection}' for connection in list_connections() or ['NONE']])
    )

@cli.command()
@click.argument('connection')
@handle_error
def list_streams(connection):
    '''
    List available streams of CONNECTION
    '''
    connection = Connection(connection)
    print_success(connection.source.available_streams)


@cli.command()
@click.argument('connection')
@click.option('--from-deployed-docker-image', is_flag=True, default=False, help="Set this flag only in a deployed docker image")
@handle_error
def run(connection, from_deployed_docker_image):
    '''
    Run Extract-Load for CONNECTION
    '''
    connection = Connection(connection, is_deployed=from_deployed_docker_image)
    connection.run()
    print_success('OK')


@cli.command()
@click.argument('connection')
@handle_error
def deploy(connection):
    '''
    Deploy CONNECTION
    '''
    connection = Connection(connection)
    connection.deploy()
    print_success('OK')