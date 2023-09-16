# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pytorch-dataset',
    'version': '0.0.3',
    'description': 'Pytorch Dataset - Pytorch',
    'long_description': "[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Pytorch-Dataset\nA PyTorch Code Dataset for Cutting-Edge Fine-tuning\n\n\n\n## Installation\nYou can install the package using pip\n\n```bash\npip install pytorch-dataset\n```\n\n# Usage\n```python\n\nfrom pytorch import GitHubDatasetGenerator\n\ngenerator = GitHubDatasetGenerator('username', 'token')\ndataset = generator.generate_dataset()\ngenerator.save_dataset(dataset, 'dataset.jsonl')\n```\n\n# License\nMIT\n\n\n\n",
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Agora-X/Pytorch-Dataset',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
