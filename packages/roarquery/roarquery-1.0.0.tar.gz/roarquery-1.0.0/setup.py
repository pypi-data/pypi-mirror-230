# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['roarquery']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'pandas>=1.4.2,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'tqdm>=4.64.0,<5.0.0']

entry_points = \
{'console_scripts': ['roarquery = roarquery.__main__:main']}

setup_kwargs = {
    'name': 'roarquery',
    'version': '1.0.0',
    'description': 'Roarquery',
    'long_description': 'Roarquery\n=========\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/roarquery.svg\n   :target: https://pypi.org/project/roarquery/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/roarquery.svg\n   :target: https://pypi.org/project/roarquery/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/roarquery\n   :target: https://pypi.org/project/roarquery\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/roarquery\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/roarquery/latest.svg?label=Read%20the%20Docs\n   :target: https://roarquery.readthedocs.io/\n   :alt: Read the documentation at https://roarquery.readthedocs.io/\n.. |Tests| image:: https://github.com/richford/roarquery/workflows/Tests/badge.svg\n   :target: https://github.com/richford/roarquery/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/richford/roarquery/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/richford/roarquery\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* Query ROAR runs\n* Download ROAR runs and trials\n* List ROAR Firestore collections\n\n\nRequirements\n------------\n\n* Python 3.9+\n* `fuego`_\n\n\nInstallation\n------------\n\nYou can install *Roarquery* via pip_ from PyPI_:\n\n.. code:: console\n\n   pip install roarquery\n\n*Roarquery* also requires you to install *fuego*, a command line firestore client.\nPlease see the `fuego documentation`_ for complete installation instructions.\n\nOn a Mac, follow these steps:\n\n1. Ensure you have a working go installation. If\n\n.. code:: console\n\n   go version\n\nreturns something, then you are good to go. If not, install go with homebrew:\n\n.. code:: console\n\n   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"\n   brew install go\n\n2. Then install *fuego*\n\n.. code:: console\n\n   git clone https://github.com/sgarciac/fuego.git\n   cd fuego\n   go build .\n   go install .\n\n3. Finally, modify your PATH variable to include the go installation directory, which can be done with the following incantation:\n\n.. code:: console\n\n   echo $HOME/go/bin | sudo tee -a /private/etc/paths.d/go\n\n4. You may need to open a new terminal window or tab for these changes to take effect.\n\nUsage\n-----\n\nAuthentication\n~~~~~~~~~~~~~~\n\nBefore you can use *Roarquery*, you need to provide authentication details:\n\n*Roarquery* works with both the current and legacy ROAR assessment databases.\nFor example, the `roarquery runs` subcommand accepts a `--legacy` parameter to access the legacy database.\nIf you would like to use roarquery with both databases, you will need to follow\nthe steps below in both the legacy and current assessment Firebase projects.\n\n1. Retrieve or generate a Service Account key file.\n\n   a. go to your `Firebase project console`_,\n   b. go to "Project settings" (in the little gear menu next to "Project Overview"),\n   c. click on the "Service accounts" tab,\n   d. click on the "Generate new private key" button.\n\n2. Save these files to somewhere on your computer. For example, presuming the previous commands downloaded the files to "$HOME/Downloads/private_key.json" and "$HOME/Downloads/legacy_private_key.json"\n\n   .. code:: bash\n\n      mkdir -p "$HOME/.firebaseconfig"\n      mv "$HOME/Downloads/private_key.json" "$HOME/.firebaseconfig/private_key.json"\n      mv "$HOME/Downloads/legacy_private_key.json" "$HOME/.firebaseconfig/legacy_private_key.json"\n\n3. Set the environment variable `ROAR_QUERY_CREDENTIALS` (or `ROAR_QUERY_LEGACY_CREDENTIALS` for the legacy database) to point to these files.\n\n   .. code:: bash\n\n      echo "export ROAR_QUERY_CREDENTIALS=\\"$HOME/.firebaseconfig/private_key.json\\"" >> ~/.zprofile\n      echo "export ROAR_QUERY_CREDENTIALS=\\"$HOME/.firebaseconfig/private_key.json\\"" >> ~/.bash_profile\n      echo "export ROAR_QUERY_LEGACY_CREDENTIALS=\\"$HOME/.firebaseconfig/legacy_private_key.json\\"" >> ~/.zprofile\n      echo "export ROAR_QUERY_LEGACY_CREDENTIALS=\\"$HOME/.firebaseconfig/legacy_private_key.json\\"" >> ~/.bash_profile\n\n\nCommand-line Usage\n~~~~~~~~~~~~~~~~~~\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Roarquery* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _authentication_instructions:\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/richford/roarquery/issues\n.. _Firebase project console: https://console.firebase.google.com\n.. _fuego: https://sgarciac.github.io/fuego/\n.. _fuego documentation: https://sgarciac.github.io/fuego/#installation\n.. _service account credentials: https://sgarciac.github.io/fuego/#authentication\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://roarquery.readthedocs.io/en/latest/usage.html\n',
    'author': 'Adam Richie-Halford',
    'author_email': 'richiehalford@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/richford/roarquery',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
