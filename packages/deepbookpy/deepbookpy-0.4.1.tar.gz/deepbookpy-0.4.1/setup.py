# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepbookpy', 'deepbookpy.types', 'deepbookpy.utils']

package_data = \
{'': ['*']}

install_requires = \
['pysui>=0.35.0,<0.36.0']

setup_kwargs = {
    'name': 'deepbookpy',
    'version': '0.4.1',
    'description': 'Sui Deepbook Python SDK',
    'long_description': '# Sui DeepBook Python SDK\nPython DeepBook Client SDK for Sui blockchain - built by community with [pysui](https://github.com/FrankC01/pysui/)\n\n## Python Sui DeepBook SDK Parameters\n```py\nfrom deepbookpy.utils.normalizer import normalize_sui_object_id\n\nCLOCK = normalize_sui_object_id("0x6")\nDEEPBOOK_PACKAGE_ID = normalize_sui_object_id("dee9")\n\n```\n## Install deepbookpy\n`pip install deepbookpy`\n\n`poetry add deepbookpy`\n\n## Documentation\nCheck out latest deepbookpy [documentation](https://deepbookpy.readthedocs.io/en/latest/) release \n\n## Official DeepBook Resources\n\n[Official Deepbook Sui Website](https://sui-deepbook.com/)\n\n[Official Deepbook Sui Documentation](https://docs.sui-deepbook.com/)\n\n## DeepBook Packages\n\n[DeepBook Mainnet Package](https://suiexplorer.com/object/0x000000000000000000000000000000000000000000000000000000000000dee9)\n\n[DeepBook Testnet Package](https://suiexplorer.com/object/0x000000000000000000000000000000000000000000000000000000000000dee9?network=testnet)\n\n[DeepBook Devnet Package](https://suiexplorer.com/object/0x000000000000000000000000000000000000000000000000000000000000dee9?network=devnet)\n\n## Ask A Question\n\nJoin Our Coummunity [discord](https://discord.gg/CUTen9zu5h)\n',
    'author': 'andreidev1',
    'author_email': 'andreid.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
