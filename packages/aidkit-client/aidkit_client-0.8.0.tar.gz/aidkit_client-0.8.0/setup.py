# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aidkit_client',
 'aidkit_client._endpoints',
 'aidkit_client.experimental',
 'aidkit_client.plotting',
 'aidkit_client.resources',
 'aidkit_client.resources.report']

package_data = \
{'': ['*']}

install_requires = \
['Pillow==8.4',
 'altair>=4.2.0,<5.0.0',
 'httpx>=0.21.1,<0.22.0',
 'ipython==7.34.0',
 'ipywidgets>=8.0.1,<9.0.0',
 'jsonschema==3.2.0',
 'matplotlib>=3.5.3,<4.0.0',
 'pandas>=1.1.4,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'tenacity>=8.2.1,<9.0.0',
 'tqdm>=4.49.0,<5.0.0']

setup_kwargs = {
    'name': 'aidkit-client',
    'version': '0.8.0',
    'description': 'aidkit for your CI/CD and j-notebooks.',
    'long_description': '![aidkit](https://www.neurocat.ai/wp-content/uploads/2018/11/addkit-hori.png)\n\naidkit is an MLOps platform that allows you to assess and defend against threads\nand vulnerabilities of AI models before they deploy to production.\naidkit-client is a companion python client library to seamlessly integrate with\naidkit in python projects.\n',
    'author': 'neurocat GmbH',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
