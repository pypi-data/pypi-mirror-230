# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pytorch-dataset',
    'version': '0.0.4',
    'description': 'Pytorch Dataset - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Pytorch-Dataset\nA PyTorch Code Dataset for Cutting-Edge Fine-tuning\n\n\n\n## Installation\nYou can install the package using pip\n\n```bash\npip install pytorch-dataset\n```\n\n# Usage\nDownloader that downloads and unzips each repository in an account\n```python\n\nfrom pytorch import GitHubRepoDownloader\n\ndownloader = GitHubRepoDownloader(username="lucidrains", download_dir="lucidrains_repositories")\ndownloader.download_repositories()\n```\n\nProcessor that cleans, formats, and submits the cleaned dataset to huggingface\n```python\nfrom pytorch import CodeDatasetBuilder\n\ncode_builder = CodeDatasetBuilder("lucidrains_repositories")\ncode_builder.save_dataset("lucidrains_python_code_dataset")\ncode_builder.push_to_hub("lucidrains_python_code_dataset", organization="kye")\n\n```\n# License\nMIT\n\n\n\n',
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
