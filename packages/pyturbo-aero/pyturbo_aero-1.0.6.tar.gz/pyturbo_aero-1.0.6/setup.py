# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyturbo', 'pyturbo.aero', 'pyturbo.helper', 'pyturbo.ml']

package_data = \
{'': ['*'],
 'pyturbo': ['wiki/2D_design/*', 'wiki/3D_design/*', 'wiki/HeatPipe/*']}

install_requires = \
['matplotlib>3.2.1',
 'numpy-stl',
 'numpy>1.23.1',
 'pandas>=1.4',
 'plotly',
 'scipy>1.8.0',
 'tqdm']

setup_kwargs = {
    'name': 'pyturbo-aero',
    'version': '1.0.6',
    'description': 'PyTurbo_Aero is a Turbomachinery blade design library that lets you create a full 3D blades and passages.',
    'long_description': 'None',
    'author': 'Paht Juangphanich',
    'author_email': 'paht.juangphanich@nasa.gov',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
