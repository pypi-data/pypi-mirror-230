# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openrpcclientgenerator']

package_data = \
{'': ['*'],
 'openrpcclientgenerator': ['templates/python/*', 'templates/typescript/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'black>=23.9.1,<24.0.0',
 'case-switcher>=1.2.1,<2.0.0',
 'httpx>=0.24.1,<0.25.0',
 'isort>=5.12.0,<6.0.0',
 'openrpc>=8.1.0,<9.0.0',
 'pydantic>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'openrpcclientgenerator',
    'version': '0.43.0',
    'description': 'Generate clients from an Open-RPC document.',
    'long_description': '# Open-RPC Client Generator\n\nGenerate clients from Open-RPC APIs.\n\n## CLI\n\nClient generator works with WebSocket and HTTP urls.\n\n```shell\norpc --url ws://localhost:8000/api/v1 --lang py\n```\n\n## Languages\n\n| Option | Language   |\n|--------|------------|\n| py     | Python     |\n| ts     | TypeScript |\n',
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/openrpc-client-generator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
