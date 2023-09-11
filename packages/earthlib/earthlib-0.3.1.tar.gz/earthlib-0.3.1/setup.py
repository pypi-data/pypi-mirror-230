# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['earthlib']

package_data = \
{'': ['*'], 'earthlib': ['data/*']}

install_requires = \
['earthengine-api>=0.1.317',
 'numpy>=1.21.5',
 'pandas>=1.3.5',
 'spectral>=0.22.4',
 'tqdm>=4.63.0']

setup_kwargs = {
    'name': 'earthlib',
    'version': '0.3.1',
    'description': 'A global spectral library with earth engine tools for satellite land cover mapping.',
    'long_description': '# earthlib\nSpectral library and unmixing tools for satellite land cover mapping.\n',
    'author': 'earth-chris',
    'author_email': 'cbanders@alumni.stanford.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
