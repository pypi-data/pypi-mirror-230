# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commitizen',
 'commitizen.commands',
 'commitizen.config',
 'commitizen.cz',
 'commitizen.cz.conventional_commits',
 'commitizen.cz.customize',
 'commitizen.cz.jira',
 'commitizen.providers']

package_data = \
{'': ['*'], 'commitizen': ['templates/*']}

install_requires = \
['argcomplete>=1.12.1,<3.2',
 'charset-normalizer>=2.1.0,<4',
 'colorama>=0.4.1,<0.5.0',
 'decli>=0.6.0,<0.7.0',
 'importlib_metadata>=4.13,<7',
 'jinja2>=2.10.3',
 'packaging>=19',
 'pyyaml>=3.08',
 'questionary>=1.4.0,<2.0.0',
 'termcolor>=1.1,<3',
 'tomlkit>=0.5.3,<1.0.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=4.0.1,<5.0.0']}

entry_points = \
{'commitizen.plugin': ['cz_conventional_commits = '
                       'commitizen.cz.conventional_commits:ConventionalCommitsCz',
                       'cz_customize = '
                       'commitizen.cz.customize:CustomizeCommitsCz',
                       'cz_jira = commitizen.cz.jira:JiraSmartCz'],
 'commitizen.provider': ['cargo = commitizen.providers:CargoProvider',
                         'commitizen = commitizen.providers:CommitizenProvider',
                         'composer = commitizen.providers:ComposerProvider',
                         'npm = commitizen.providers:NpmProvider',
                         'pep621 = commitizen.providers:Pep621Provider',
                         'poetry = commitizen.providers:PoetryProvider',
                         'scm = commitizen.providers:ScmProvider'],
 'commitizen.scheme': ['pep440 = commitizen.version_schemes:Pep440',
                       'semver = commitizen.version_schemes:SemVer'],
 'console_scripts': ['cz = commitizen.cli:main',
                     'git-cz = commitizen.cli:main']}

setup_kwargs = {
    'name': 'commitizen',
    'version': '3.9.0',
    'description': 'Python commitizen client tool',
    'long_description': '[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/commitizen-tools/commitizen/pythonpackage.yml?label=python%20package&logo=github&logoColor=white&style=flat-square)](https://github.com/commitizen-tools/commitizen/actions)\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)\n[![PyPI Package latest release](https://img.shields.io/pypi/v/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)\n[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/commitizen?style=flat-square)](https://pypi.org/project/commitizen/)\n[![Supported versions](https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)\n[![homebrew](https://img.shields.io/homebrew/v/commitizen?color=teal&style=flat-square)](https://formulae.brew.sh/formula/commitizen)\n[![Codecov](https://img.shields.io/codecov/c/github/commitizen-tools/commitizen.svg?style=flat-square)](https://codecov.io/gh/commitizen-tools/commitizen)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n![Using commitizen cli](images/demo.gif)\n\n---\n\n**Documentation:** [https://commitizen-tools.github.io/commitizen/](https://commitizen-tools.github.io/commitizen/)\n\n---\n\n## About\n\nCommitizen is release management tool designed for teams.\n\nCommitizen assumes your team uses a standard way of committing rules\nand from that foundation, it can bump your project\'s version, create\nthe changelog, and update files.\n\nBy default, commitizen uses [conventional commits][conventional_commits], but you\ncan build your own set of rules, and publish them.\n\nUsing a standardized set of rules to write commits, makes commits easier to read, and enforces writing\ndescriptive commits.\n\n### Features\n\n- Command-line utility to create commits with your rules. Defaults: [Conventional commits][conventional_commits]\n- Bump version automatically using [semantic versioning][semver] based on the commits. [Read More](./bump.md)\n- Generate a changelog using [Keep a changelog][keepchangelog]\n- Update your project\'s version files automatically\n- Display information about your commit rules (commands: schema, example, info)\n- Create your own set of rules and publish them to pip. Read more on [Customization](./customization.md)\n\n## Requirements\n\n[Python](https://www.python.org/downloads/) `3.7+`\n\n[Git][gitscm] `1.8.5.2+`\n\n## Installation\n\nTo make commitizen available in your system\n\n```bash\npip install --user -U Commitizen\n```\n\n### Python project\n\nYou can add it to your local project using one of these:\n\n```bash\npip install -U commitizen\n```\n\nfor Poetry >= 1.2.0:\n\n```bash\npoetry add commitizen --group dev\n```\n\nfor Poetry < 1.2.0:\n\n```bash\npoetry add commitizen --dev\n```\n\n### macOS\n\nvia [homebrew](https://formulae.brew.sh/formula/commitizen):\n\n```bash\nbrew install commitizen\n```\n\n## Usage\n\nMost of the time this is the only command you\'ll run:\n\n```sh\ncz bump\n```\n\nOn top of that, you can use commitizen to assist you with the creation of commits:\n\n```sh\ncz commit\n```\n\nRead more in the section [Getting Started](./getting_started.md).\n\n### Help\n\n```sh\n$ cz --help\nusage: cz [-h] [--debug] [-n NAME] [-nr NO_RAISE] {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version} ...\n\nCommitizen is a cli tool to generate conventional commits.\nFor more information about the topic go to https://conventionalcommits.org/\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --debug               use debug mode\n  -n NAME, --name NAME  use the given commitizen (default: cz_conventional_commits)\n  -nr NO_RAISE, --no-raise NO_RAISE\n                        comma separated error codes that won\'t rise error, e.g: cz -nr 1,2,3 bump. See codes at https://commitizen-\n                        tools.github.io/commitizen/exit_codes/\n\ncommands:\n  {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version}\n    init                init commitizen configuration\n    commit (c)          create new commit\n    ls                  show available commitizens\n    example             show commit example\n    info                show information about the cz\n    schema              show commit schema\n    bump                bump semantic version based on the git log\n    changelog (ch)      generate changelog (note that it will overwrite existing file)\n    check               validates that a commit message matches the commitizen schema\n    version             get the version of the installed commitizen or the current project (default: installed commitizen)\n```\n\n## Setting up bash completion\n\nWhen using bash as your shell (limited support for zsh, fish, and tcsh is available), Commitizen can use [argcomplete](https://kislyuk.github.io/argcomplete/) for auto-completion. For this argcomplete needs to be enabled.\n\nargcomplete is installed when you install Commitizen since it\'s a dependency.\n\nIf Commitizen is installed globally, global activation can be executed:\n\n```bash\nsudo activate-global-python-argcomplete\n```\n\nFor permanent (but not global) Commitizen activation, use:\n\n```bash\nregister-python-argcomplete cz >> ~/.bashrc\n```\n\nFor one-time activation of argcomplete for Commitizen only, use:\n\n```bash\neval "$(register-python-argcomplete cz)"\n```\n\nFor further information on activation, please visit the [argcomplete website](https://kislyuk.github.io/argcomplete/).\n\n## Sponsors\n\nThese are our cool sponsors!\n\n<!-- sponsors --><!-- sponsors -->\n\n[conventional_commits]: https://www.conventionalcommits.org\n[semver]: https://semver.org/\n[keepchangelog]: https://keepachangelog.com/\n[gitscm]: https://git-scm.com/downloads\n',
    'author': 'Santiago Fraire',
    'author_email': 'santiwilly@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/commitizen-tools/commitizen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
