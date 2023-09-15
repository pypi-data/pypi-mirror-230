import pathlib
import toml
from .generation import push_generation
from .config import HARDCODED


def create_netlink_defaults():
    path = pathlib.Path.home() / ".netlink"
    path.mkdir(exist_ok=True)
    path = path / "default.toml"
    if path.exists():
        push_generation(path)
    with path.open("w", encoding="utf-8") as f:
        toml.dump(HARDCODED, f)
