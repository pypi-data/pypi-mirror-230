# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['next']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'omnimodal',
    'version': '0.0.1',
    'description': 'NextGPT - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Next GPT\nImplementation of "NExT-GPT: Any-to-Any Multimodal LLM",\n\nPaper Link\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n# Install\n`pip install next-gpt`\n\n# Usage\n\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n\n# Citations\n```BibTeX\n@articles{wu2023nextgpt,\n  title={NExT-GPT: Any-to-Any Multimodal LLM},\n  author={Shengqiong Wu, Hao Fei, Leigang Qu, Wei Ji, Tat-Seng Chua},\n  journal = {CoRR},\n  volume = {abs/2309.05519},\n  year={2023}\n}\n```',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/NExT-GPT',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
