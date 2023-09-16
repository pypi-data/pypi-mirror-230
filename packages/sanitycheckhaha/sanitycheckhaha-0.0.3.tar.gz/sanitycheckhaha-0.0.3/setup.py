# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sanitycheckhaha']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['sanitycheckhaha = sanitycheckhaha.sanitycheckhaha:main']}

setup_kwargs = {
    'name': 'sanitycheckhaha',
    'version': '0.0.3',
    'description': 'Test of a commandline feature python package',
    'long_description': '[![check](https://github.com/retospect/wibble/actions/workflows/check.yml/badge.svg)](https://github.com/retospect/wibble/actions/workflows/check.yml)\n# Wibble - a template for simple python packages\n\n\nA minimalist template for a python package.\n\nProvides the bl and the blarg commands, \nand does basic continuous integraton testing on github.\n\nMake a copy of the project, and fix the replacements below.\n\n## Things to replace\n\n- ```grep -ri word .``` will find the *word* in all the files\n- ```find . | grep word``` will find the *word* in any filenames\n- *retospect* - changed to your github user name\n- *wibble* - change to the name of your project\n- *wobble* - change to the internal package name you want to use \n- *fafa* - change to whatever your commandline command should be if you are providing a script\n- update the pyproject.py file to have your name and the right description. \n',
    'author': 'Tyler Gaw',
    'author_email': None,
    'maintainer': 'Tyler Gaw',
    'maintainer_email': None,
    'url': 'https://github.com/tagaw/sanitycheckhaha',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
