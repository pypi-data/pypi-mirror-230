# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kraken_analytics_rmq']

package_data = \
{'': ['*']}

install_requires = \
['pika>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'kraken-analytics-rmq',
    'version': '1.0.0',
    'description': 'kraken analytics rabbitmq client',
    'long_description': '',
    'author': 'Thomas',
    'author_email': 'thomas@kraken-analytics.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/stakkle5/kraken-analytics-rmq',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
