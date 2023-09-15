# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pynteracta', 'pynteracta.cli', 'pynteracta.schemas']

package_data = \
{'': ['*']}

install_requires = \
['pydantic-settings-toml>=0.2.0,<0.3.0',
 'pydantic-settings>=2.0.0,<3.0.0',
 'pydantic[email]>=2.0,<3.0',
 'pyjwt[crypto]>=2.6.0,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'typer>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['pynta = pynteracta.cli.commands:app']}

setup_kwargs = {
    'name': 'pynteracta',
    'version': '0.3.4',
    'description': 'A wrapper for Interacta API',
    'long_description': "PYnteracta, utility e wrapper per api di Interacta\n---------------------------------------------------\n\nUtility e libreria wrapper open-source in linguaggio Python per l'interfacciamento con le api rest\ndi [Interacta](https://catalogocloud.agid.gov.it/service/1892).\n\n\nInstallazione\n-------------\n\n```\npython -m pip install pynteracta\n```\n\nUtilizzo utility command line\n-----------------------------\n\nPynteracta ha un'interfaccia a riga di comando per verificare l'accesso ad un ambiente di produzione di Interacta.\n\nE' supportato lo schema di autenticazione Server-to-Serveril per mezzo di Service Account: ```\n\n- [Service Account](https://injenia.atlassian.net/wiki/spaces/IEAD/pages/3624075265/Autenticazione#Autenticazione-via-Service-Account-(Server-to-Server))\n```\n\nLista dei primi 10 post della community identificata dall'id passata come parametro\n\n    $ pynta --env **TOML_ENV_FILE** get-community-definition\n```\n\nLista dei primi 10 post della community identificata dall'id passata come parametro\n\n    $ pynta -e **PATH_CONF_TOML**  list-posts **COMMUNITY-ID**\n",
    'author': 'Simone Dalla',
    'author_email': 'simodalla@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/simodalla/pynteracta',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
