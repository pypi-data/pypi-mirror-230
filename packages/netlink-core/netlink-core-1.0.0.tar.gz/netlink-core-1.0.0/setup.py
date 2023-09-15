# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['core']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0', 'toml>=0.10.2']

entry_points = \
{'console_scripts': ['create_netlink_defaults = '
                     'netlink.core.cli:create_netlink_defaults']}

setup_kwargs = {
    'name': 'netlink-core',
    'version': '1.0.0',
    'description': 'Core components of NetLink tools',
    'long_description': "# netlink-core\n\nCore components of NetLink tools\n\n## Updates\n\n### 0.0.4\n\nAdd `netlink.core.Mapping` Abstract class, must implement `__init__`.\n\nThis provides a small set of functionality share by my collection of tools:\n\n- [netlink-crypt](https://pypi.org/project/netlink-crypt/)\n- [netlink-logging](https://pypi.org/project/netlink-logging/)\n- [netlink-sap-rfc](https://pypi.org/project/netlink-sap-rfc/)\n- [netlink-sharepoint](https://pypi.org/project/netlink-sharepoint/)\n\n## Contents\n\n- Centralized configuration using [TOML](https://toml.io/en/)\n  in the users home directory (subdirectory `.netlink`).\n\n### Classes\n\n#### netlink.core.AttributeMapping\n\nbehaves like an immutable mapping, adding access to all items via property notation:\n\n      a['b'] == a.b\n\nThis is propagated through all levels, when parameter `deep` is `True` (default):\n\n      a['b']['c']['d'] == a.b.c.d\n\n| Parameter      | Default        |                                                                                               |\n|----------------|----------------|-----------------------------------------------------------------------------------------------|\n| value          | **mandatory**  | Mapping containing information. Might be deep.                                                |\n| deep           | `True`         | Items within the mapping will be copied, not referenced (implemented for Lists and Mappings). |\n| case_sensitive | `False`        | If **False**, ignore case when retrieving items or attributes.                                |\n| under          | `True`         | Try dash (`-`) if underscore (`_`) in name not found. |\n\n#### netlink.core.Singleton\n\nis a base class to be inherited from to make all instances of a class the same.\n\n#### netlink.core.Config\n\nis a Singleton that provides configuration information (will be initialized the first time).\n\n### Scripts\n\n- `create_netlink_defaults` creates a TOML file containing all currently internal defaults in the users home directory (\n  subdirectory `.netlink`). If the file already exist, the current file is copied as a backup with extension `.001`.\n\n## Installation\n\nUse your preferred tool to install from [PyPI](https://pypi.org/). I prefer [Poetry](https://python-poetry.org/).\n\n[//]: # (## Roadmap)\n\n[//]: # (## Contributing)\n\n## License\n\nMIT\n",
    'author': 'Bernhard Radermacher',
    'author_email': 'bernhard.radermacher@netlink-consulting.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/netlink_python/netlink-core.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
