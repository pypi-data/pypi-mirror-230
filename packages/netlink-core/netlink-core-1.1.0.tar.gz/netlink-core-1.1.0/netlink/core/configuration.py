import pathlib
from typing import Callable

import toml
import yaml

from .mapping import Mapping
from .singleton import Singleton


class Configuration(Singleton, Mapping):
    """Configuration for different applications. Provides option to inherit for defined sections."""

    _initialized = False

    def __init__(self, configuration_name: str, default_config: Callable[[], dict]):
        if not self._initialized:
            self.configuration_path = pathlib.Path.home() / '.netlink'
            self.configuration_name = configuration_name
            self._data = self._get_configuration_file(configuration_name, default_config)
            self._initialized = True
        if configuration_name not in self._data:
            self._data[configuration_name] = self._get_configuration_file(configuration_name, default_config)

    def _get_configuration_file(self, name: str, default_config: Callable[[], dict]):
        if (self.configuration_path / name).with_suffix('.toml').exists():
            return toml.load((self.configuration_path / name).with_suffix('.toml'))
        if (self.configuration_path / name).with_suffix('yaml').exists():
            with (self.configuration_path / name).with_suffix('yaml').open('r', encoding='utf-8-sig') as f:
                return yaml.safe_load(f)
        # neither .toml nor .yaml was found: use callback to create .toml
        data = default_config()
        with (self.configuration_path / name).with_suffix('.toml').open('w', encoding='utf-8') as f:
            toml.dump(data, f)
        return data
