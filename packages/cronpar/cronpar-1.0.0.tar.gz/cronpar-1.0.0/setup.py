# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cronpar']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.7,<9.0.0']

entry_points = \
{'console_scripts': ['cronpar = cronpar.cli:main']}

setup_kwargs = {
    'name': 'cronpar',
    'version': '1.0.0',
    'description': 'A Cron Expression Parser',
    'long_description': '# Cronpar - a tool for parsing cron expression\n\n### Requirements\n\nTo run this program, you need setup you local environment as following\n\n- A Python Environment with Python 3.8+ and pip (reckon use pyenv and create a virtualenv)\n- Poetry (Dependency management)\n- make (a dev tool)\n\n### Setup\n\nBefore you can run everything, please make sure you have setup a Python environment\n\nif you are using make, you can setup the dev environmane by simply using\n\n```shell\nmake init\n```\n\nthis will install poetry and install all dependencies. If you don\'t want to use make, alternatively, just run the \nfollowing commands\n\n```shell\npip install poetry\npoetry install\n```\n\nTo prepare/build the cli tool for you to play with, run\n\n```shell\nmake build\n```\n\nor, just run\n\n```shell\npipx install .\n```\n\nNow, you should be able to run the program, for example\n\n```shell\ncronpar explain "*/15 0 1,15 * 1-5 /usr/bin/find"\n```\n\n### Yesting & Contribution\n\nThere are some test cases generated during development, to run the tests, you can either run\n\n```shell\nmake test\n```\n\npr \n\n```shell\npoetry run pytest tests/ --cov --cov-fail-under 89\n```\n\nPlease make sure you have tested all the changes you made properly, and all tests passed before you push\n\nAlso, it will be good to keep the code formatted, you can check this by running\n\n```shell\nmake format\nmake lint\n```\n\nor \n\n```shell\npoetry run black --preview --line-length 120 cronpar\npoetry run isort --line-length 120 cronpar\npoetry run flakehell lint .\n```\n\n### Notice\n\nPlease Note this program is still in development, it may be not very stable,\nbut we will fix and add more features in the coming future.\n',
    'author': 'Liusha He',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.12',
}


setup(**setup_kwargs)
