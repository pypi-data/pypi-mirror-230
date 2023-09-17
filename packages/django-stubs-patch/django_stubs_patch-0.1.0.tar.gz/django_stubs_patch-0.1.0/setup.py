# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_stubs_patch']

package_data = \
{'': ['*']}

install_requires = \
['django-stubs==1.9.0', 'django==3.2.12', 'mypy>=0.971,<0.972']

setup_kwargs = {
    'name': 'django-stubs-patch',
    'version': '0.1.0',
    'description': 'A pmypy django-stubs patch work for python3.6',
    'long_description': '# django-stubs-patch\n\n[![Release](https://img.shields.io/github/v/release/mrlyc/django-stubs-patch)](https://img.shields.io/github/v/release/mrlyc/django-stubs-patch)\n[![Build status](https://img.shields.io/github/actions/workflow/status/mrlyc/django-stubs-patch/main.yml?branch=main)](https://github.com/mrlyc/django-stubs-patch/actions/workflows/main.yml?query=branch%3Amain)\n[![codecov](https://codecov.io/gh/mrlyc/django-stubs-patch/branch/main/graph/badge.svg)](https://codecov.io/gh/mrlyc/django-stubs-patch)\n[![Commit activity](https://img.shields.io/github/commit-activity/m/mrlyc/django-stubs-patch)](https://img.shields.io/github/commit-activity/m/mrlyc/django-stubs-patch)\n[![License](https://img.shields.io/github/license/mrlyc/django-stubs-patch)](https://img.shields.io/github/license/mrlyc/django-stubs-patch)\n\nA pmypy django-stubs patch work for python3.6\n\n- **Github repository**: <https://github.com/mrlyc/django-stubs-patch/>\n- **Documentation** <https://mrlyc.github.io/django-stubs-patch/>\n\n## Getting started with your project\n\nFirst, create a repository on GitHub with the same name as this project, and then run the following commands:\n\n``` bash\ngit init -b main\ngit add .\ngit commit -m "init commit"\ngit remote add origin git@github.com:mrlyc/django-stubs-patch.git\ngit push -u origin main\n```\n\nFinally, install the environment and the pre-commit hooks with\n\n```bash\nmake install\n```\n\nYou are now ready to start development on your project! The CI/CD\npipeline will be triggered when you open a pull request, merge to main,\nor when you create a new release.\n\nTo finalize the set-up for publishing to PyPi or Artifactory, see\n[here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).\nFor activating the automatic documentation with MkDocs, see\n[here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).\nTo enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).\n\n## Releasing a new version\n\n- Create an API Token on [Pypi](https://pypi.org/).\n- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting\n[this page](https://github.com/mrlyc/django-stubs-patch/settings/secrets/actions/new).\n- Create a [new release](https://github.com/mrlyc/django-stubs-patch/releases/new) on Github.\nCreate a new tag in the form ``*.*.*``.\n\nFor more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).\n\n---\n\nRepository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).\n',
    'author': 'MrLYC',
    'author_email': 'fimyikong@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mrlyc/django-stubs-patch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
