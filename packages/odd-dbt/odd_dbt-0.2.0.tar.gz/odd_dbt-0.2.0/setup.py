# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odd_dbt',
 'odd_dbt.domain',
 'odd_dbt.mapper',
 'odd_dbt.service',
 'odd_dbt.utils']

package_data = \
{'': ['*']}

install_requires = \
['dbt-postgres>=1.6.2,<2.0.0',
 'dbt-snowflake>=1.6.2,<2.0.0',
 'funcy>=2.0,<3.0',
 'loguru>=0.6.0,<0.7.0',
 'odd-models>=2.0.31,<3.0.0',
 'oddrn-generator>=0.1.93,<0.2.0',
 'psycopg2-binary>=2.9.6,<3.0.0',
 'sqlalchemy>=1.4.46,<2.0.0',
 'typer[all]>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['odd_dbt_test = odd_dbt.app:app']}

setup_kwargs = {
    'name': 'odd-dbt',
    'version': '0.2.0',
    'description': 'OpenDataDiscovery Action for dbt',
    'long_description': "# OpenDataDiscovery dbt tests metadata collecting\n\n[![PyPI version](https://badge.fury.io/py/odd-dbt.svg)](https://badge.fury.io/py/odd-dbt)\n\nCLI tool helps run and ingest dbt test to platform.\n\nIt can be used as separated CLI tool or within [ODD CLI](https://github.com/opendatadiscovery/odd-cli) package which\nprovides some useful additional features for working with OpenDataDiscovery.\n\n## Supported adapters\n\n| Adapter   | version |\n|-----------|---------|\n| Snowflake | ^1.6    |\n| Postgres  | ^1.6    |\n\nProfiles inside the file looks different for each type of data source.\n\n**Snowflake** host_settings value is created from field `account`. Field value should be `<account_identifier>`\nFor example the URL for an account uses the following format: `<account_identifier>`.snowflakecomputing.com\nExample Snowflake account identifier `hj1234.eu-central-1`.\n\n## Supported tests types\n\n1. [x]  Generic tests\n2. [ ] Singular tests. Currently Singular tests are not supported.\n\n## Installation\n```pip install odd-dbt```\n\n## To see all available commands\n```\nodd_dbt_test --help\n```\n\n## Example\nFor each command that involves sending information to OpenDataDiscovery platform exists set of env variables:\n1. `ODD_PLATFORM_HOST` - Where you platform is\n2. `ODD_PLATFORM_TOKEN` - Token for ingesting data to platform (How to create [token](https://docs.opendatadiscovery.org/configuration-and-deployment/trylocally#create-collector-entity)?)\n3. `DBT_DATA_SOURCE_ODDRN` - Unique oddrn string describes dbt source, i.e '//dbt/host/localhost'\n\nIt is recommended to add them as ENV variables or provide as flags to each command\n```\nexport ODD_PLATFORM_HOST=http://localhost:8080\nexport ODD_PLATFORM_TOKEN=token***\nexport DBT_DATA_SOURCE_ODDRN=//dbt/host/localhost\n```\n\n### Commands\n`create-datasource` - helps to register dbt as data source at OpenDataDiscovery platform. User later for ingesting metadata.\n```commandline\nodd_dbt_test create-datasource --name=my_local_dbt --dbt-host=localhost\n```\n\n`ingest-test` - Read results_run file under the target folder to parse and ingest metadata.\n```commandline\nodd_dbt_test ingest-test --profile=my_profile\n```\n\n`test` - Proxy command to `dbt test`, then reads results_run file under the target folder to parse and ingest metadata.\n```commandline\nodd_dbt_test test --profile=my_profile\n```\n\n### Run commands programmatically\nYou could run that scrip to read, parse and ingest test results to the platform.\n```python\n# ingest_test_result.py\nfrom odd_dbt import config\nfrom odd_dbt.domain.cli_args import CliArgs\nfrom odd_dbt.service.dbt import get_context\nfrom odd_dbt.service.odd import ingest_entities\nfrom odd_dbt.mapper.test_results import DbtTestMapper\n\ncfg = config.Config() # All fields can be set manually or read from ENV variables\nclient = config.create_odd_client(host=cfg.odd_platform_host, token=cfg.odd_platform_token)\ngenerator = config.create_dbt_generator_from_oddrn(oddrn=cfg.dbt_data_source_oddrn)\n\ncli_args = CliArgs.default()\ncontext = get_context(cli_args=cli_args)\ndata_entities = DbtTestMapper(context=context, generator=generator).map()\ningest_entities(data_entities, client)\n```",
    'author': 'Mateusz Kulas',
    'author_email': 'mkulas@provectus.com',
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
