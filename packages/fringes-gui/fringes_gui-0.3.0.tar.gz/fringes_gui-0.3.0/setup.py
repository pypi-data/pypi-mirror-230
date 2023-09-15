# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fringes_gui']

package_data = \
{'': ['*']}

install_requires = \
['asdf>=2.14.3,<3.0.0',
 'fringes>=0.3.0,<0.3.1',
 'opencv-contrib-python>=4.7.0,<5.0.0',
 'pyqt6>=6.4.2,<7.0.0',
 'pyqtgraph>=0.13.2,<0.14.0',
 'pyyaml>=6.0,<7.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'fringes-gui',
    'version': '0.3.0',
    'description': "Graphical user interface for the 'fringes' package.",
    'long_description': '# Fringes-GUI\n![PyPI](https://img.shields.io/pypi/v/fringes-gui)\n![GitHub top language](https://img.shields.io/github/languages/top/comimag/fringes-gui)\n![Read the Docs](https://img.shields.io/readthedocs/fringes)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![PyPI - License](https://img.shields.io/pypi/l/fringes-gui)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/fringes-gui)\n\nGraphical user interface for the [fringes](https://pypi.org/project/fringes/) package.\n\n## Installation\nYou can install `fringes-gui` directly from [PyPi](https://pypi.org/project/fringes-gui) via `pip`:\n\n```\npip install fringes-gui\n```\n\n## Usage\nYou import the `fringes-gui` package and call the function `run()`.\n\n```python\nimport fringes_gui as fgui\nfgui.run()\n```\n\nNow the graphical user interface should appear:\n\n![Screenshot](https://raw.githubusercontent.com/comimag/fringes/main/docs/getting_started/GUI.png)\\\nScreenshot of the GUI.\n\n## Documentation\nThe documentation can be found here:\nhttps://fringes.readthedocs.io/en/latest/getting_started/usage.html#graphical-user-interface\n\n## License\nCreative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License\n',
    'author': 'Christian Kludt',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/comimag/fringes-gui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
