# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['googleapiwrapper']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client==2.31.0',
 'google-auth-httplib2==0.1.0',
 'google-auth-oauthlib==0.4.6',
 'gspread>=5.1.1',
 'oauth2client>=4.1.3,<5.0.0',
 'python-common-lib==1.0.8']

setup_kwargs = {
    'name': 'google-api-wrapper2',
    'version': '1.0.7',
    'description': '',
    'long_description': '# google-api-wrapper\n\nRun ./setup.sh to set up git pre/post push hook scripts.\nThen, a similar script loaded to the environment will execute the pre/post push hook scripts: \nhttps://stackoverflow.com/a/3812238/1106893\n\nFor example loading this script and defining an alias like this will do the trick:\n`alias gpwh="git-push-with-hooks.sh"`\n\n\n## Setup of precommit\n\nConfigure precommit as described in this blogpost: https://ljvmiranda921.github.io/notebook/2018/06/21/precommits-using-black-and-flake8/\nCommands:\n1. Install precommit: `pip install pre-commit`\n2. Make sure to add pre-commit to your path. For example, on a Mac system, pre-commit is installed here: \n   `$HOME/Library/Python/3.8/bin/pre-commit`.\n2. Execute `pre-commit install` to install git hooks in your `.git/` directory.\n\n## Troubleshooting\n\n### Installation issues\nIn case you\'re facing a similar issue:\n```\nAn error has occurred: InvalidManifestError: \n=====> /<userhome>/.cache/pre-commit/repoBP08UH/.pre-commit-hooks.yaml does not exist\nCheck the log at /<userhome>/.cache/pre-commit/pre-commit.log\n```\n, please run: `pre-commit autoupdate`\nMore info here: https://github.com/pre-commit/pre-commit/issues/577',
    'author': 'Szilard Nemeth',
    'author_email': 'szilard.nemeth88@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
