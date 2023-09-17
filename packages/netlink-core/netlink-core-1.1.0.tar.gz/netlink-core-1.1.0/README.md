# netlink-core

Core components of NetLink tools

## Updates

### 0.0.4

Add `netlink.core.Mapping` Abstract class, must implement `__init__`.

This provides a small set of functionality share by my collection of tools:

- [netlink-crypt](https://pypi.org/project/netlink-crypt/)
- [netlink-logging](https://pypi.org/project/netlink-logging/)
- [netlink-sap-rfc](https://pypi.org/project/netlink-sap-rfc/)
- [netlink-sharepoint](https://pypi.org/project/netlink-sharepoint/)

## Contents

- Centralized configuration using [TOML](https://toml.io/en/)
  in the users home directory (subdirectory `.netlink`).

### Classes

#### netlink.core.AttributeMapping

behaves like an immutable mapping, adding access to all items via property notation:

      a['b'] == a.b

This is propagated through all levels, when parameter `deep` is `True` (default):

      a['b']['c']['d'] == a.b.c.d

| Parameter      | Default        |                                                                                               |
|----------------|----------------|-----------------------------------------------------------------------------------------------|
| value          | **mandatory**  | Mapping containing information. Might be deep.                                                |
| deep           | `True`         | Items within the mapping will be copied, not referenced (implemented for Lists and Mappings). |
| case_sensitive | `False`        | If **False**, ignore case when retrieving items or attributes.                                |
| under          | `True`         | Try dash (`-`) if underscore (`_`) in name not found. |

#### netlink.core.Singleton

is a base class to be inherited from to make all instances of a class the same.

#### netlink.core.Config

is a Singleton that provides configuration information (will be initialized the first time).

### Scripts

- `create_netlink_defaults` creates a TOML file containing all currently internal defaults in the users home directory (
  subdirectory `.netlink`). If the file already exist, the current file is copied as a backup with extension `.001`.

## Installation

Use your preferred tool to install from [PyPI](https://pypi.org/). I prefer [Poetry](https://python-poetry.org/).

[//]: # (## Roadmap)

[//]: # (## Contributing)

## License

MIT
