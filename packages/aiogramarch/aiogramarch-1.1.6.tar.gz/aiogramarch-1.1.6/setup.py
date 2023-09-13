# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiogramarch',
 'aiogramarch.templates',
 'aiogramarch.templates.apps.app',
 'aiogramarch.templates.apps.app.{{ cookiecutter.app_name }}',
 'aiogramarch.templates.core.admin',
 'aiogramarch.templates.core.contrib.payments.freekassa',
 'aiogramarch.templates.core.contrib.user',
 'aiogramarch.templates.project',
 'aiogramarch.templates.project.{{ cookiecutter.project_name }}',
 'aiogramarch.templates.project.{{ cookiecutter.project_name }}.src',
 'aiogramarch.templates.project.{{ cookiecutter.project_name }}.src.core',
 'aiogramarch.templates.project.{{ cookiecutter.project_name '
 '}}.src.core.database',
 'aiogramarch.templates.project.{{ cookiecutter.project_name }}.src.core.orm',
 'aiogramarch.templates.project.{{ cookiecutter.project_name }}.src.core.utils',
 'aiogramarch.templates.project.{{ cookiecutter.project_name }}.src.main']

package_data = \
{'': ['*'],
 'aiogramarch.templates': ['core/admin/templates/*',
                           'core/admin/templates/providers/login/*']}

install_requires = \
['aiogram>=3.0.0b',
 'click>=8.1.3',
 'cookiecutter>=2.1.1',
 'loguru>=0.6.0',
 'pydantic==1.10.12']

entry_points = \
{'console_scripts': ['aiogramarch = aiogramarch.cli.app:cli']}

setup_kwargs = {
    'name': 'aiogramarch',
    'version': '1.1.6',
    'description': 'Managing aiogram projects',
    'long_description': '# <p align="center"> Aiogramarch </p>\n<p align="center">Project manager and generator for Aiogram</p>\n\n\n\n\n## Installation\n\n``` python\npip install aiogramarch\n```\n\n## How to use\n\n``` bash\naiogramarch startproject [projectname]\n```\n\n``` bash\ncd codingbot\n```\n\n``` bash\naiogramarch startapp [appname]\n```\n\n``` bash\naiogramarch includeRedis\n```\n\n``` bash\naiogramarch includeFastApi\n```\n\n``` bash\naiogramarch includeAdmin\n```\n\n#### To find out all the functions:\n\n``` bash\naiogramarch --help\n```\n\n\n',
    'author': 'BulatXam',
    'author_email': 'Khamdbulat@yandex.ru',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
