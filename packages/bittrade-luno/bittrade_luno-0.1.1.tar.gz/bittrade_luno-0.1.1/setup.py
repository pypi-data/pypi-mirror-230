# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bittrade_luno',
 'bittrade_luno.connection',
 'bittrade_luno.framework',
 'bittrade_luno.models',
 'bittrade_luno.models.rest',
 'bittrade_luno.rest']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.3,<4.0.0',
 'ccxt==2.6.5',
 'elm-framework-helpers>=0.3.1,<0.4.0',
 'expression>=4.2.4,<5.0.0',
 'orjson>=3.9.4,<4.0.0',
 'prompt-toolkit>=3.0.39,<4.0.0',
 'ptpython>=3.0.23,<4.0.0',
 'pydantic==1.10.12',
 'reactivex>=4.0.4,<5.0.0',
 'requests>=2.31.0,<3.0.0',
 'rich>=13.5.2,<14.0.0',
 'websocket-client>=1.6.1,<2.0.0',
 'websockets>=10.4,<11.0']

setup_kwargs = {
    'name': 'bittrade-luno',
    'version': '0.1.1',
    'description': 'Reactive for luno',
    'long_description': '# bittrade luno\n> rxpy based LUNO stream and rest api',
    'author': 'Yu Jin',
    'author_email': 'adamlyj89@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
