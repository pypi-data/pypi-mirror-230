# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bumbag']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0', 'toolz>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'bumbag',
    'version': '5.1.0',
    'description': 'A package for Python utility functions.',
    'long_description': '<p align="center">\n<img src="https://raw.githubusercontent.com/estripling/bumbag/main/docs/source/_static/logo.png" width="180" alt="The BumBag logo.">\n</p>\n\n<p align="center">\n<a href="https://pypi.org/project/bumbag"><img alt="pypi" src="https://img.shields.io/pypi/v/bumbag"></a>\n<a href="https://readthedocs.org/projects/bumbag/?badge=latest"><img alt="docs" src="https://readthedocs.org/projects/bumbag/badge/?version=latest"></a>\n<a href="https://github.com/estripling/bumbag/actions/workflows/ci.yml"><img alt="ci status" src="https://github.com/estripling/bumbag/actions/workflows/ci.yml/badge.svg?branch=main"></a>\n<a href="https://codecov.io/gh/estripling/bumbag"><img alt="coverage" src="https://codecov.io/github/estripling/bumbag/coverage.svg?branch=main"></a>\n<a href="https://github.com/estripling/bumbag/blob/main/LICENSE"><img alt="license" src="https://img.shields.io/pypi/l/bumbag"></a>\n</p>\n\n## About\n\nBumBag is a collection of Python utility functions:\n\n- [Documentation](https://bumbag.readthedocs.io/en/stable/index.html)\n- [Example usage](https://bumbag.readthedocs.io/en/stable/example.html)\n- [API Reference](https://bumbag.readthedocs.io/en/stable/autoapi/bumbag/index.html)\n\n## Installation\n\n`bumbag` is available on [PyPI](https://pypi.org/project/bumbag/) for Python 3.8+:\n\n```shell\npip install bumbag\n```\n\n## Examples\n\nEasily [`flatten`](https://bumbag.readthedocs.io/en/stable/autoapi/bumbag/index.html#bumbag.flatten) an irregular list:\n\n```python\n>>> import bumbag\n>>> irregular_list = [\n...     ["one", 2],\n...     3,\n...     [(4, "five")],\n...     [[["six"]]],\n...     "seven",\n...     [],\n... ]\n>>> list(bumbag.flatten(irregular_list, 8, [9, ("ten",)]))\n[\'one\', 2, 3, 4, \'five\', \'six\', \'seven\', 8, 9, \'ten\']\n```\n\nUse [`highlight_string_differences`](https://bumbag.readthedocs.io/en/stable/autoapi/bumbag/index.html#bumbag.highlight_string_differences) to see differences between two strings easily:\n\n```python\n>>> import bumbag\n>>> print(bumbag.highlight_string_differences("hello", "hall"))\nhello\n |  |\nhall\n```\n\nQuickly compare two Python sets with [`two_set_summary`](https://bumbag.readthedocs.io/en/stable/autoapi/bumbag/index.html#bumbag.two_set_summary):\n\n```python\n>>> import bumbag\n>>> x = {"a", "c", "b", "g", "h"}\n>>> y = {"c", "d", "e", "f", "g"}\n>>> summary = bumbag.two_set_summary(x, y)\n>>> print(summary["report"])\n    x (n=5): {\'a\', \'b\', \'c\', ...}\n    y (n=5): {\'c\', \'d\', \'e\', ...}\nx | y (n=8): {\'a\', \'b\', \'c\', ...}\nx & y (n=2): {\'c\', \'g\'}\nx - y (n=3): {\'a\', \'b\', \'h\'}\ny - x (n=3): {\'d\', \'e\', \'f\'}\nx ^ y (n=6): {\'a\', \'b\', \'d\', ...}\njaccard = 0.25\noverlap = 0.4\ndice = 0.4\ndisjoint?: False\nx == y: False\nx <= y: False\nx <  y: False\ny <= x: False\ny <  x: False\n```\n\n## Contributing to BumBag\n\nYour contribution is greatly appreciated!\nSee the following links to help you get started:\n\n- [Contributing Guide](https://bumbag.readthedocs.io/en/latest/contributing.html)\n- [Developer Guide](https://bumbag.readthedocs.io/en/latest/developers.html)\n- [Contributor Code of Conduct](https://bumbag.readthedocs.io/en/latest/conduct.html)\n\n## License\n\n`bumbag` was created by the BumBag Developers.\nIt is licensed under the terms of the BSD 3-Clause license.\n',
    'author': 'BumBag Developers',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/estripling/bumbag',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
