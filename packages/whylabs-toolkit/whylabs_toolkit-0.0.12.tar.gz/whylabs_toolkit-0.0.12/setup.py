# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whylabs_toolkit',
 'whylabs_toolkit.cli',
 'whylabs_toolkit.container',
 'whylabs_toolkit.helpers',
 'whylabs_toolkit.monitor',
 'whylabs_toolkit.monitor.manager',
 'whylabs_toolkit.monitor.models',
 'whylabs_toolkit.monitor.models.analyzer',
 'whylabs_toolkit.utils']

package_data = \
{'': ['*'], 'whylabs_toolkit.monitor': ['schema/*']}

install_requires = \
['jsonschema>=4.17.3,<5.0.0',
 'pydantic>=1.10.4,<2.0.0',
 'whylabs-client>=0.5,<0.6',
 'whylogs>=1.1.26,<2.0.0']

setup_kwargs = {
    'name': 'whylabs-toolkit',
    'version': '0.0.12',
    'description': 'Whylabs CLI and Helpers package.',
    'long_description': "# WhyLabs Toolkit\n\nThe WhyLabs Toolkit package contains helper methods to help users interact with our internal APIs. Users will benefit from using it if they want to abstract some of WhyLabs' internal logic and also automate recurring API calls.\n\n\n## Basic usage\nTo start using the `whylabs_toolkit` package, install it from PyPI with:\n```bash\npip install whylabs_toolkit\n``` \n\n## Packages\n\nThe available packages that we have enable different use-cases for the `whylabs_toolkit`. To get started, navigate to one of the following sections and find useful tutorials there.\n\n| Package             | Usage                |\n|---------------------|----------------------|\n| [Monitor Manager](https://github.com/whylabs/whylabs-toolkit/blob/mainline/whylabs_toolkit/monitor/manager/README.md) | Author and modify existing WhyLabs monitor with Python |\n| [WhyLabs Helpers](https://github.com/whylabs/whylabs-toolkit/blob/mainline/whylabs_toolkit/helpers/README.md) | Interact with and modify your Datasets and ML Models specs in WhyLabs. |\n\n## Development\n\nTo start contributing, you will manage dependencies with [Poetry](https://python-poetry.org/) and also a handful of `Makefile` commands. To install all necessary dependencies and activate the virtual environment, run:\n\n```bash\nmake setup && poetry shell\n```\n\n## Get in touch\nIf you want to learn more how you can benefit from this package or if there is anything missing, please [contact our support](https://whylabs.ai/contact-us), we'll be more than happy to help you!",
    'author': 'Anthony Naddeo',
    'author_email': 'anthony.naddeo@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
