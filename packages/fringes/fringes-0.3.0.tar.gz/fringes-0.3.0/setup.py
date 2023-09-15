# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fringes']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0',
 'asdf>=2.14.3,<3.0.0',
 'numba>=0.57.1,<0.58.0',
 'numpy>=1.23.5,<2.0.0',
 'opencv-contrib-python>=4.7.0,<5.0.0',
 'pyyaml>=6.0,<7.0',
 'scikit-image>=0.21.0,<0.22.0',
 'scipy>=1.10.0,<2.0.0',
 'si-prefix>=1.2.2,<2.0.0',
 'sympy>=1.11.1,<2.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'fringes',
    'version': '0.3.0',
    'description': 'Phase shifting algorithms for encoding and decoding sinusoidal fringe patterns.',
    'long_description': '# Fringes\n[![PyPI](https://img.shields.io/pypi/v/fringes)](https://pypi.org/project/fringes/)\n![GitHub top language](https://img.shields.io/github/languages/top/comimag/fringes)\n[![Read the Docs](https://img.shields.io/readthedocs/fringes)](https://fringes.readthedocs.io)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI - License](https://img.shields.io/pypi/l/fringes)](https://github.com/comimag/fringes/blob/main/LICENSE.txt)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/fringes)\n\n<!---\n![GitHub issues](https://img.shields.io/github/issues/comimag/fringes)\n![GitHub](https://img.shields.io/github/license/comimag/fringes)\n--->\n\n<!---\nlink to  paper, please cite\n--->\n\nEasy to use tool for generating and analyzing fringe patterns with phase shifting algorithms.\n\n![Coding Scheme](https://raw.githubusercontent.com/comimag/fringes/main/docs/getting_started/coding-scheme.gif)\\\nPhase Shift Coding Scheme.\n\n## Installation\nYou can install `fringes` directly from [PyPi](https://pypi.org/) via `pip`:\n\n```\npip install fringes\n```\n\n## Usage\nYou instantiate, parameterize and deploy the `Fringes` class:\n\n```python\nimport fringes as frng  # import module\n\nf = frng.Fringes()      # instantiate class\n\nf.glossary              # get glossary\nf.X = 1920              # set width of the fringe patterns\nf.Y = 1080              # set height of the fringe patterns\nf.K = 2                 # set number of sets\nf.N = 4                 # set number of shifts\nf.v = [9, 10]           # set spatial frequencies\nf.T                     # get number of frames\n                            \nI = f.encode()          # encode fringe patterns\nA, B, x = f.decode(I)   # decode fringe patterns\n```\n\nAll [parameters](https://fringes.readthedocs.io/en/latest/user_guide/params.html)\nare accesible by the respective attributes of the `Fringes` instance\n(a glossary of them is obtained by the attribute `glossary`).\nThey are implemented as class properties (managed attributes).\nNote that some attributes have subdependencies, hence dependent attributes might change as well.\nCircular dependencies are resolved automatically.\n\nFor generating the fringe pattern sequence `I`, use the method `encode()`.\\\nIt returns a [NumPy array](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) \nin videoshape (frames `T`, width `X`, height `Y`, color channels `C`).\n\nFor analyzing (recorded) fringe patterns, use the method `decode()`.\\\nIt returns the Numpy arrays brightness `A`, modulation `B` and coordinate `x`.\n\n## Graphical User Interface\nDo you need a GUI? `Fringes` has a sister project which is called `Fringes-GUI`:\nhttps://pypi.org/project/fringes-gui/\n\n## Documentation\nThe documentation can be found here:\nhttps://fringes.readthedocs.io\n\n## Troubleshooting\n- __Decoding takes a long time__  \n  This is most likely due to the just-in-time compiler [Numba](https://numba.pydata.org/), \n  which is used for this computationally expensive function:\n  During the first execution, an initial compilation is executed. \n  This can take several tens of seconds up to single digit minutes, depending on your CPU.\n  However, for any subsequent execution, the compiled code is cached and the code of the function runs much faster, \n  approaching the speeds of code written in C.\n\n## License\nCreative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License\n',
    'author': 'Christian Kludt',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/comimag/fringes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.13',
}


setup(**setup_kwargs)
