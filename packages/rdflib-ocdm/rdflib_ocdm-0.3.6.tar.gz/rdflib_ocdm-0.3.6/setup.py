# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rdflib_ocdm', 'rdflib_ocdm.counter_handler', 'rdflib_ocdm.prov']

package_data = \
{'': ['*']}

install_requires = \
['oc-ocdm>=7.1.7,<8.0.0',
 'rdflib>=6.2.0,<7.0.0',
 'redis>=4.5.5,<5.0.0',
 'sparqlwrapper>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'rdflib-ocdm',
    'version': '0.3.6',
    'description': '',
    'long_description': '[<img src="https://img.shields.io/badge/powered%20by-OpenCitations-%239931FC?labelColor=2D22DE" />](http://opencitations.net)\n[![Run tests](https://github.com/opencitations/rdflib-ocdm/actions/workflows/run_tests.yml/badge.svg)](https://github.com/opencitations/rdflib-ocdm/actions/workflows/run_tests.yml)\n![Coverage](https://raw.githubusercontent.com/opencitations/rdflib-ocdm/main/test/coverage/coverage.svg)\n![PyPI](https://img.shields.io/pypi/pyversions/rdflib-ocdm)\n![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/opencitations/rdflib-ocdm)\n\n# rdflib-ocdm\n',
    'author': 'arcangelo7',
    'author_email': 'arcangelomas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.4,<4.0.0',
}


setup(**setup_kwargs)
