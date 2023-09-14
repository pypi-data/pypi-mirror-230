# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auxiliary', 'auxiliary.nifti', 'auxiliary.normalization', 'auxiliary.tiff']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=10.0.0,<11.0.0',
 'nibabel>3.0',
 'numpy>=1.25,<2.0',
 'path>=16.7.1,<17.0.0',
 'pathlib>=1.0,<2.0',
 'tifffile>2023.8.25']

setup_kwargs = {
    'name': 'auxiliary',
    'version': '0.0.29',
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
