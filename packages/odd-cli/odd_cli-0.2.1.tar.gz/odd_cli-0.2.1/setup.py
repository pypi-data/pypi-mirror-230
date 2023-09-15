# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odd_cli',
 'odd_cli.apps',
 'odd_cli.reader',
 'odd_cli.reader.mapper',
 'odd_cli.reader.models']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0',
 'odd-dbt>=0.2.1,<0.3.0',
 'odd-models>=2.0.31,<3.0.0',
 'oddrn-generator>=0.1.92,<0.2.0',
 'pyarrow>=10.0.1,<11.0.0',
 'tqdm>=4.64.1,<5.0.0',
 'typer[all]>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['odd = odd_cli.main:app']}

setup_kwargs = {
    'name': 'odd-cli',
    'version': '0.2.1',
    'description': 'Command line tool for working with OpenDataDiscovery. ',
    'long_description': "## OpenDataDiscovery CLI\n[![PyPI version](https://badge.fury.io/py/odd-cli.svg)](https://badge.fury.io/py/odd-cli)\n\nCommand line tool for working with OpenDataDiscovery.\nIt makes it easy to create token though console and ingest local dataset's metadata to OpenDataDiscovery platform.\n\n## Installation\n```bash\npip install odd-cli\n```\n\n#### Available commands\n```text\n╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮\n│ --install-completion          Install completion for the current shell.                                              │\n│ --show-completion             Show completion for the current shell, to copy it or customize the installation        │\n╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯\n╭─ Commands ─────────────────────────────────────────────────────────────────────────────────╮\n│ collect                       Collect and ingest metadata for local files from folder      │\n│ dbt                           Run dbt tests and inject results to ODD platform             │\n│ tokens                        Manipulate OpenDataDiscovery platform's tokens               │\n╰────────────────────────────────────────────────────────────────────────────────────────────╯\n```\n## Env variables used for commands\n\n`ODD_PLATFORM_HOST` - Location of OpenDataDiscovery Platform.\n\n`ODD_PLATFORM_TOKEN` - Collector token, can be created using [UI](https://docs.opendatadiscovery.org/configuration-and-deployment/trylocally#create-collector-entity) or `odd tokens create` command.\n\n## Commands\nCreate collector token.\n```bash\nodd tokens create <collector_name>\n```\n\nParse and ingest local files\n```bash\nodd collect <path_to_folder_with_datasets>\n```\n\nRun dbt tests and inject results to ODD platform. It uses [odd-dbt](https://github.com/opendatadiscovery/odd-dbt) package.\n```bash\nodd dbt test <path_to_dbt_project>\n```\n",
    'author': 'Pavel Makarichev',
    'author_email': 'vixtir90@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
