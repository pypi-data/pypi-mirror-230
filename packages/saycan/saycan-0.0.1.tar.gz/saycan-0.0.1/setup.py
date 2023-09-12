# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saycan']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'saycan',
    'version': '0.0.1',
    'description': 'Paper - Pytorch',
    'long_description': "[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Python Package Template\nA easy, reliable, fluid template for python packages complete with docs, testing suites, readme's, github workflows, linting and much much more\n\n\n## Installation\n\nYou can install the package using pip\n\n```bash\npip install saycan\n```\n## Usage\n```\n\n\n```\n\n# License\nMIT\n\n\n\n",
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/paper',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
