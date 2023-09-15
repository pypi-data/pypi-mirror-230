import pathlib
import toml

from .attribute_mapping import AttributeMapping
from .singleton import Singleton

KILOBYTE = 1024
MEGABYTE = 1024 * KILOBYTE

HARDCODED = {
    "logging": {
        "level": 20,
        "message_format": "%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "file_format": "[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s",
        "file_size": 100 * MEGABYTE,
        "file_generations": 5,
    },
}

CONFIG_PATH = pathlib.Path.home() / ".netlink"

MANDATORY = tuple(['logging', ])

_default = HARDCODED.copy()
if (CONFIG_PATH / "default.toml").exists():
    with (CONFIG_PATH / "default.toml").open("r", encoding="utf-8-sig") as f:
        _default.update(toml.load(f))


class Config(AttributeMapping, Singleton):

    def __init__(self, application: str = None):
        if not self._data:
            data = {}
            if application and application.lower() != 'default':  # get data from possible section in default.toml
                data = {k: v for k, v in _default.get(application, {}).items()}
                if CONFIG_PATH.exists():  # there might be a separate config file
                    application_path = CONFIG_PATH / f"{application}.toml"
                    if application_path.exists():
                        with application_path.open("r") as f:
                            data.update(toml.load(f))
            for i in MANDATORY:  # load any missing mandatory sections
                if i not in data:
                    data[i] = {k: v for k, v in _default[i].items()}
            super(Config, self).__init__(data, deep=True, case_sensitive=False, under=True)
