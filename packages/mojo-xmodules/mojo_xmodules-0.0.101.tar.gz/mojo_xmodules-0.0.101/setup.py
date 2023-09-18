# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'source/packages'}

packages = \
['mojo',
 'mojo.xmods',
 'mojo.xmods.credentials',
 'mojo.xmods.eventing',
 'mojo.xmods.extension',
 'mojo.xmods.interfaces',
 'mojo.xmods.landscaping',
 'mojo.xmods.landscaping.agents',
 'mojo.xmods.landscaping.client',
 'mojo.xmods.landscaping.cluster',
 'mojo.xmods.landscaping.coordinators',
 'mojo.xmods.landscaping.coupling',
 'mojo.xmods.landscaping.layers',
 'mojo.xmods.landscaping.service',
 'mojo.xmods.modeling',
 'mojo.xmods.wellknown',
 'mojo.xmods.wrappers',
 'mojo.xmods.xlogging',
 'mojo.xmods.xmultiprocessing',
 'mojo.xmods.xthreading']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.5,<9.0.0',
 'debugpy>=1.6.6,<2.0.0',
 'mojo-collections>=0.0.11,<0.1.0',
 'mojo-config>=0.0.20,<0.1.0',
 'mojo-errors>=0.0.2,<1.0.0',
 'mojo-waiting>=1.1.0,<2.0.0',
 'paramiko>=3.1.0,<4.0.0']

setup_kwargs = {
    'name': 'mojo-xmodules',
    'version': '0.0.101',
    'description': 'Automation Mojo X-Modules',
    'long_description': '\n=========================================\nAutomation Mojo X-Modules (mojo-xmodules)\n=========================================\n\nThis package contains helper modules that extend the function of standard python modules.\n\n==========\nReferences\n==========\n\n- `User Guide <userguide/userguide.rst>`_\n- `Coding Standards <userguide/10-00-coding-standards.rst>`_\n\n\n',
    'author': 'Myron Walker',
    'author_email': 'myron.walker@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'http://automationmojo.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
