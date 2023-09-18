# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cybex']

package_data = \
{'': ['*']}

install_requires = \
['openai']

setup_kwargs = {
    'name': 'cybex',
    'version': '0.0.2',
    'description': 'Cybex - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Cybex\nAutonomously generate high-quality unit tests for entire repositories, just plug in and play the repo link and enjoy high quality tests to elevate your project\n\n\n## Installation\n`pip install cybex`\n\n\n## Usage\n```python\nfrom cybex import TestGenerator\n\n# Example usage:\ntest_generator = TestGenerator(\n    repo_url="https://github.com/kyegomez/exa", \n    api_key=""\n)\ntest_generator.download()\ntest_generator.generate_tests()\n```\n\n# License\nMIT\n\n\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/Cybex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
