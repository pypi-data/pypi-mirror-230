# Easy Configuration Manager for Python applications
## Configuration made easy

When you need some configuration, or you need sets of configuration 
to correspond to more stages such as development, test and production 
you may want to have a single configuration set and refer to it 
all over your application.

Then you may want to incorporate your set of configration buckets
into your CLI application.

## installation

### install the package on your environment
using pip:
```shell
$ pip install pyconfman
```

### Incorporate it into your application
If you use `click` library to manage your application CLI
there is already, `pyconfman` comes along with a simple function to add
the config group to your application's `cli.group`. 

For example, if your app has a command such as
```python
import click
@click.group()
def cli():
    """My amazing application"""

if __name__ == "__main__":
    cli()
```

you can incorporate the `confman` as following:

```python
import click
import pyconfman


@pyconfman.cli
@click.group()
def cli():
    """My amazing application"""


if __name__ == "__main__":
    cli()
```
This adds the configuration manager to your command line interface

## Usage and command line

```
$ myapp --help

Usage: myapp [OPTIONS] COMMAND [ARGS]...

Options:
  -C, --conf-dir TEXT  configuration directory: [~/.config/<myapp>]
  --help               Show this message and exit.

Commands:
  config  Read or modify configuration files.
  ...
  ...
```

### Get configs on the spot 

```shell
Usage: myapp config [OPTIONS] COMMAND [ARGS]...

  Read or modify configuration files.

Options:
  --help  Show this message and exit.

Commands:
  get   Print out configuration information.
  load  Load a full configuration storage from `path_to_json` file.
  set   Set a single value on a configuration storage
```
