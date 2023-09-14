# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['suinspy', 'suinspy.type', 'suinspy.utils']

package_data = \
{'': ['*']}

install_requires = \
['pysui>=0.35.0,<0.36.0', 'requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'suinspy',
    'version': '0.2.1',
    'description': 'Sui Name Service Python SDK Client',
    'long_description': '# Sui Name Service Python SDK\n\nPython Sui Name Service SDK Client - built by community with [pysui](https://github.com/FrankC01/pysui/)\n\n## Quick Start\n\nInstall `suinspy`\n\n`pip install suinspy`\n\n`poetry add suinspy`\n\nUsing git support:\n\n`pip install git+https://git@github.com/andreidev1/suinspy.git`\n\nConfigure `pysui` with your own data.\n\n```py\nfrom pysui.sui.sui_config import SuiConfig\nfrom pysui.sui.sui_clients.sync_client import SuiClient\n\ndef cfg_user():\n    """Config user"""\n    cfg = SuiConfig.user_config(\n        # Required\n        rpc_url="https://fullnode.mainnet.sui.io:443/",\n        # Must be a valid Sui keystring (i.e. \'key_type_flag | private_key_seed\' )\n        prv_keys=["AIUPxQvxM18QggDDdTO0D0OD6PNVvtet50072d1grIyl"],\n        # Needed for subscribing\n        ws_url="wss://fullnode.mainnet.sui.io:443/",\n    )\n    return cfg\n\ncfg = cfg_user()\nclient = SuiClient(cfg)\n\n```\n\nImport `suinspy`\n```py\nfrom suinspy.client import SuiNsClient\n```\n\nCreate an instance of SuinsClient and choose network type (`mainet`, `testnet` or `devnet`).\n\n```py\nsuins = SuiNsClient(client, \'mainet\')\n```\n\nFetch a name object:\n```py\nsuins.get_name_object("suins.sui")\n```\n\nFetch a name object including the owner and avatar:\n\n**_NOTE:_** `show_owner` and `show_avatar` arguments are optional.\n```py\nsuins.get_name_object("suins.sui", show_owner=True, show_avatar=True)\n```\n\nFetch a SuiAddress linked to a name:\n```py\nsuins.get_address("suins.sui")\n```\n\n## Official SuiNS Resources\n\n[Official SuiNS Website](https://suins.io/)\n\n[Official SuiNS Discord](https://discord.gg/suinsdapp)\n\n## Ask A Question\n\nJoin Our Community [discord](https://discord.gg/CUTen9zu5h)\n',
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
