# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inpainting']

package_data = \
{'': ['*']}

install_requires = \
['nibabel>3.0',
 'numpy>=1.25,<2.0',
 'torch>=2.0.1,<3.0.0',
 'torchmetrics>=1.1.2,<2.0.0']

setup_kwargs = {
    'name': 'inpainting',
    'version': '0.0.1',
    'description': 'TODO.',
    'long_description': None,
    'author': 'Florian Kofler',
    'author_email': 'florian.kofler@tum.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
