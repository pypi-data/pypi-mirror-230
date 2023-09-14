"""CLI management for a pluggable Configuration CLI."""
import os
import sys

import click
from click import style

from pyconfman.manager import DEFAULT_CONF_DIR, Config


def get_config(force=False) -> 'Config':
    ctx = click.get_current_context()
    path = ctx.obj and ctx.obj.get('conf_dir')
    path = path or DEFAULT_CONF_DIR
    if not force and not os.path.exists(path):
        click.echo(f'Configuration directory {style(path, fg="red")} doesn\'t exists.')
        sys.exit(2)
    return Config(path)


def add_config_cli(group: click.Group):  # pylint: disable=too-complex
    """Add `config` group to your Click CLI."""

    def print_config_list(config):
        for conf in config:
            click.echo(''.join((style(' - ', fg='green'), conf)))
        for conf in config.sub_confs:
            click.echo(f' {style("+", fg="yellow")} {conf}')

    @group.group()
    def config():
        """Read or modify configuration files."""

    @config.command()
    @click.argument('path', default=None, required=True)
    @click.option('-o', '--output', default=None)
    def get(path, output):
        """Print out configuration information."""
        def repr_dict(obj, lev=0):
            pre = 4 * lev
            ml = max(len(str(key)) for key in obj) if obj else 1
            for key, val in sorted(obj.items()):
                if isinstance(val, list) and val:
                    val = {f'● {n}': v for n, v in enumerate(val)}
                if isinstance(val, dict):
                    click.echo(f"{' ':<{pre}}{style(key, fg='red'):<{ml + 9}}: 👇")
                    repr_dict(val, lev + 1)
                else:
                    click.echo(f"{' ':>{pre}}{style(key, fg='red'):<{ml + 9}}: {style(val, bold=True)}")

        config = get_config()
        try:
            result = config.get(path)
        except KeyError:
            click.echo(f'Configuration for {style(path, fg="red")} not found.')
            sys.exit(3)
        output = output.lower() if output else ''
        valid_outputs = {'yaml', 'json'}
        if output and output.lower() in valid_outputs:
            if output == 'json':
                import json  # pylint: disable=import-outside-toplevel
                print(json.dumps(result, sort_keys=True, indent=4))
                sys.exit(0)
            if output == 'yaml':
                import yaml  # pylint: disable=import-outside-toplevel
                print(yaml.dump(result))
                sys.exit(0)
        if isinstance(result, list):
            result = {f'- {n}': v for n, v in enumerate(result)}
        if isinstance(result, dict):
            repr_dict(result)
        elif isinstance(result, (int, str)):
            click.echo(f"{style(path, fg='red')}: {style(result, bold=True)}")
        elif isinstance(result, Config):
            print_config_list(result)

    @config.command()
    @click.argument('path', default=None, required=True)
    @click.argument('value', default=None, required=True)
    def set(path, value):  # pylint: disable=redefined-builtin
        """Set a single value on a configuration storage"""
        conf = get_config()
        try:
            conf.set_key(path, value)
        except FileNotFoundError:
            click.echo(f'File {style(value, fg="red")} not found.')
            sys.exit(4)

    @config.command()
    @click.argument('path', default=None, required=True)
    @click.argument('path_to_json', default=None, required=True)
    def load(path, path_to_json):
        """Load a full configuration storage from `path_to_json` file."""
        conf = get_config()
        try:
            conf.load(path, path_to_json)
        except FileNotFoundError:
            click.echo(f'File {style(path_to_json, fg="red")} not found.')
            sys.exit(5)
    return group
