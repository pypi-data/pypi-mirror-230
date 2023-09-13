# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fathomnet', 'fathomnet.api', 'fathomnet.models', 'fathomnet.scripts']

package_data = \
{'': ['*']}

install_requires = \
['coco-lib>=0.1.2,<0.2.0',
 'dataclasses-json>=0.5.4,<0.6.0',
 'lxml>=4.6.0,<5.0.0',
 'progressbar2>=3.37.0,<4.0.0',
 'requests>=2.20.0,<3.0.0']

extras_require = \
{'models': ['appdirs>=1.4.4,<2.0.0',
            'torch>=2.0.1,<3.0.0',
            'opencv-python>=4.7.0,<5.0.0',
            'pandas>=2.0.3,<3.0.0',
            'pillow>=10.0.0,<11.0.0',
            'psutil>=5.9.5,<6.0.0',
            'torchvision>=0.15.2,<0.16.0',
            'pyyaml>=6.0.1,<7.0.0',
            'tqdm>=4.65.0,<5.0.0',
            'ultralytics>=8.0.146,<9.0.0',
            'gitpython>=3.1.32,<4.0.0']}

entry_points = \
{'console_scripts': ['fathomnet-generate = '
                     'fathomnet.scripts.fathomnet_generate:main']}

setup_kwargs = {
    'name': 'fathomnet',
    'version': '1.1.1',
    'description': 'fathomnet-py is a client-side API to help scientists, researchers, and developers interact with FathomNet data.',
    'long_description': "# fathomnet-py\n\n**`fathomnet-py`** is a client-side API to help scientists, researchers, and developers interact with [FathomNet](https://fathomnet.org/) data.\n\n```python\n>>> from fathomnet.api import boundingboxes\n>>> boundingboxes.find_concepts()\n['2G Robotics structured light laser', '55-gallon drum', ...]\n>>> from fathomnet.api import images\n>>> images.find_by_concept('Nanomia')\n[\n    AImageDTO(\n        id=2274942, \n        uuid='cdbfca66-284f-48ac-a36f-7b2ac2b43533', \n        url='https://fathomnet.org/static/m3/framegrabs/MiniROV/images/0056/02_18_37_20.png', \n        ...\n    ),\n    ...\n]\n>>> from fathomnet.api import taxa\n>>> taxa.find_children('mbari', 'Bathochordaeus')\n[\n    Taxa(name='Bathochordaeus stygius', rank='species'), \n    Taxa(name='Bathochordaeus charon', rank='species'), \n    Taxa(name='Bathochordaeus mcnutti', rank='species')\n]\n>>> from fathomnet.api import xapikey\n>>> xapikey.auth('NuCLjlNUlgHchtgDB01Sp1fABJVcWR')  # your API key here\nAuthHeader(\n    type='Bearer', \n    token='eyJhbGciOiJI...'\n)\n```\n\nThe `fathomnet-py` API offers native Python interaction with the FathomNet REST API, abstracting away the underlying HTTP requests.\n\n[![CI](https://github.com/fathomnet/fathomnet-py/actions/workflows/ci.yml/badge.svg)](https://github.com/fathomnet/fathomnet-py/actions/workflows/ci.yml)\n[![Documentation Status](https://readthedocs.org/projects/fathomnet-py/badge/?version=latest)](https://fathomnet-py.readthedocs.io/en/latest/?badge=latest)\n[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fathomnet/fathomnet-py/blob/main/tutorial.ipynb)\n## Installing `fathomnet-py`\n\n`fathomnet-py` is available on PyPI:\n\n```bash\n$ python -m pip install fathomnet\n```\n\n## API Reference available on [Read the Docs](https://fathomnet-py.readthedocs.io/)\n",
    'author': 'Kevin Barnard',
    'author_email': 'kbarnard@mbari.org',
    'maintainer': 'Kevin Barnard',
    'maintainer_email': 'kbarnard@mbari.org',
    'url': 'https://github.com/fathomnet/fathomnet-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
