"""Configuration Manager"""
from __future__ import annotations

import json
import os.path

DEFAULT_CONF_DIR = f'{os.environ["HOME"]}/.config/confman'


class ConfigError(KeyError):
    """General error in configuration manager."""


def read_json(file_name):
    """Read a json file and returns its content."""
    with open(file_name, 'r', encoding='utf-8') as in_file:
        return json.load(in_file)


def write_json(file_name, content):
    """Write `content` to `file_name` in JSON format."""
    with open(file_name, 'w', encoding='utf-8') as out_file:
        json.dump(content, out_file, indent=4, sort_keys=True)


class Config:
    """Main Configuration management Class."""
    _instances = {}  # replace it with weak dictionary

    def __init__(self, config_dir=None):
        self._keys = {}
        self._instances[config_dir] = self
        if config_dir is None:
            config_dir = DEFAULT_CONF_DIR
        self._dir = config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def __new__(cls, *args, **kwargs):
        config_dir = kwargs.pop('config_dir', None)
        if not config_dir and args:
            config_dir = args[0]
        if config_dir in cls._instances:
            return cls._instances[config_dir]
        return object.__new__(cls)

    def __getitem__(self, item):
        if item not in self._keys:
            dir_path = os.path.join(self._dir, item)
            if os.path.isdir(dir_path):
                return Config(dir_path)
            file_path = os.path.join(self._dir, f'{item}.json')
            if not os.path.exists(file_path):
                raise KeyError(f'file {file_path} not found')
            self._keys[item] = read_json(file_path)
        return self._keys[item]

    def __setitem__(self, key, value):
        self._keys[key] = value
        file_path = os.path.join(self._dir, f'{key}.json')
        write_json(file_path, value)

    def __iter__(self):
        return (f[:-5] for f in os.listdir(self._dir) if f.endswith('.json'))

    def __repr__(self):
        return f'Config("{self._dir}")'

    def __contains__(self, item):
        return (item in self._keys or
                os.path.exists(os.path.join(self._dir, item)) or
                os.path.exists(os.path.join(self._dir, f'{item}.json')))

    def get(self, path: str) -> 'Config' | dict | list | int | str:
        """Return dict-like content of a giver configuration `path`"""
        node = self
        for step in path.split('.'):
            node = node[step]
        return node

    def set_key(self, path: str, value: str | int | list | dict | tuple):
        """Find the node from the specified `path` and set its value to `value`."""
        ppath = path.split('.')
        key_to_set = ppath.pop()
        node, conf, key, mpath, _ = self._split_path('.'.join(ppath))
        if mpath == ppath:
            raise ConfigError('Nothing matches this schema')
        if isinstance(node, dict):
            if not node:
                main = node
                for step in mpath:
                    node[step] = node = {}
                node[key_to_set] = value
                conf[key] = main
            else:
                node[key_to_set] = value
                conf[key] = conf[key]  # This will save the dict JSON
        else:
            raise NotImplementedError

    def _split_path(self, path) -> ('Config' | dict, 'Config', str, list, list):
        """Break down any given `path` into parts and return the individual parts.

        - Last node in the path
        - Last Config object crossed by the path
        - The Config's object referral key
        - Non-existing steps on the path
        - Existing steps from the last Config object.
        """
        node = last_conf = self
        conf_key = None
        missing_path = []
        exiting_path = []
        for step in path.split('.'):
            if step not in node:
                node = {}  # pylint: disable=redefined-variable-type
                missing_path.append(step)
                continue
            if isinstance(node, Config):
                conf_key = step
            node = node[step]
            if isinstance(node, Config):
                last_conf = node
            elif isinstance(node, dict):
                exiting_path.append(step)
        return node, last_conf, conf_key, missing_path, exiting_path

    def load(self, config_path: str, filepath: str | list | tuple | dict):
        """Load a json file into a configuration."""
        _, conf, key, missing_path, _ = self._split_path(config_path)
        last_key = missing_path.pop() if missing_path else key
        conf_dir = os.path.join(conf._dir, *missing_path)
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)
        if isinstance(filepath, str):
            with open(filepath, 'rb') as in_file:
                loaded_dict = json.load(in_file)
        elif isinstance(filepath, (dict, list, tuple)):
            loaded_dict = filepath
        else:
            loaded_dict = None
            raise ConfigError(f'Unassignable value for key {config_path}: {filepath}')
        conf = Config(conf_dir)
        conf[last_key] = loaded_dict

    @property
    def sub_confs(self):
        """Collect sub Config objects from sub-folders."""
        return {f: Config(os.path.join(self._dir, f))
                for f in os.listdir(self._dir) if os.path.isdir(os.path.join(self._dir, f))}
