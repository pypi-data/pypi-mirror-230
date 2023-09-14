# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vima']

package_data = \
{'': ['*']}

install_requires = \
['torch']

setup_kwargs = {
    'name': 'vima',
    'version': '0.0.2',
    'description': 'vima - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# VIM\nA simple implementation of "VIMA: General Robot Manipulation with Multimodal Prompts"\n\n[Original implementation Link](https://github.com/vimalabs/VIMA)\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n# Install\n`pip install vima`\n\n---\n\n# Usage\n```python\nimport torch\nfrom vima import Vima\n\n# Generate a random input sequence\nx = torch.randint(0, 256, (1, 1024)).cuda()\n\n# Initialize VIMA model\nmodel = Vima()\n\n# Pass the input sequence through the model\noutput = model(x)\n```\n\n## MultiModal Iteration\n* Pass in text and and image tensors into vima\n```python\nimport torch\nfrom vima.vima import VimaMultiModal\n\n#usage\nimg = torch.randn(1, 3, 256, 256)\ntext = torch.randint(0, 20000, (1, 1024))\n\n\nmodel = VimaMultiModal()\noutput = model(text, img)\n\n```\n\n# License\nMIT\n\n# Citations\n```latex\n@inproceedings{jiang2023vima,\n  title     = {VIMA: General Robot Manipulation with Multimodal Prompts},\n  author    = {Yunfan Jiang and Agrim Gupta and Zichen Zhang and Guanzhi Wang and Yongqiang Dou and Yanjun Chen and Li Fei-Fei and Anima Anandkumar and Yuke Zhu and Linxi Fan},\n  booktitle = {Fortieth International Conference on Machine Learning},\n  year      = {2023}\n}\n```',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/vima',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
