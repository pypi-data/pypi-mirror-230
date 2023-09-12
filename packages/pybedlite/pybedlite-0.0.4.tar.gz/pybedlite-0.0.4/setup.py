# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cgranges', 'cgranges.test', 'pybedlite', 'pybedlite.tests']

package_data = \
{'': ['*'],
 'cgranges': ['.pytest_cache/*',
              '.pytest_cache/v/cache/*',
              'cpp/*',
              'python/*'],
 'cgranges.test': ['3rd-party/*',
                   '3rd-party/AIList/*',
                   '3rd-party/AITree/*',
                   '3rd-party/NCList/*']}

install_requires = \
['attrs>=23.0.0,<24.0.0']

extras_require = \
{'docs': ['sphinx>=7.0.0,<8.0.0']}

setup_kwargs = {
    'name': 'pybedlite',
    'version': '0.0.4',
    'description': 'Python classes for interfacing with bed intervals',
    'long_description': '\n[![Language][language-badge]][language-link]\n[![Code Style][code-style-badge]][code-style-link]\n[![Type Checked][type-checking-badge]][type-checking-link]\n[![PEP8][pep-8-badge]][pep-8-link]\n[![Code Coverage][code-coverage-badge]][code-coverage-link]\n[![License][license-badge]][license-link]\n\n---\n\n[![Python package][python-package-badge]][python-package-link]\n[![PyPI version][pypi-badge]][pypi-link]\n[![PyPI download total][pypi-downloads-badge]][pypi-downloads-link]\n\n---\n\n[language-badge]:       http://img.shields.io/badge/language-python-brightgreen.svg\n[language-link]:        http://www.python.org/\n[code-style-badge]:     https://img.shields.io/badge/code%20style-black-000000.svg\n[code-style-link]:      https://black.readthedocs.io/en/stable/ \n[type-checking-badge]:  http://www.mypy-lang.org/static/mypy_badge.svg\n[type-checking-link]:   http://mypy-lang.org/\n[pep-8-badge]:          https://img.shields.io/badge/code%20style-pep8-brightgreen.svg\n[pep-8-link]:           https://www.python.org/dev/peps/pep-0008/\n[code-coverage-badge]:  https://codecov.io/gh/fulcrumgenomics/pybedlite/branch/main/graph/badge.svg\n[code-coverage-link]:   https://codecov.io/gh/fulcrumgenomics/pybedlite\n[license-badge]:        http://img.shields.io/badge/license-MIT-blue.svg\n[license-link]:         https://github.com/fulcrumgenomics/pybedlite/blob/main/LICENSE\n[python-package-badge]: https://github.com/fulcrumgenomics/pybedlite/workflows/Python%20package/badge.svg\n[python-package-link]:  https://github.com/fulcrumgenomics/pybedlite/actions?query=workflow%3A%22Python+package%22\n[pypi-badge]:           https://badge.fury.io/py/pybedlite.svg\n[pypi-link]:            https://pypi.python.org/pypi/pybedlite\n[pypi-downloads-badge]: https://img.shields.io/pypi/dm/pybedlite\n[pypi-downloads-link]:  https://pypi.python.org/pypi/pybedlite\n\n# pybedlite\n\nSee documentation on [pybedlite.readthedocs.org][rtd-link].\n\n```\nconda install -c bioconda pybedlite\n```\nOR\n```\nconda create -n pybedlite pybedlite\nconda activate pybedlite\n```\n\nNote that while there is a version of pybedlite on pypi versions of pybedlite >=\n0.0.2 cannot at present be installed via pypi because they have dependencies\nthat preclude publishing to pypi. For this reason installation via conda is\nrequired.\n\n[rtd-link]:    http://pybedlite.readthedocs.org/en/stable\n\n**Requires python 3.8+** (for python < 3.8, please use pybedlite <= 0.0.3)\n\n# Getting Setup for Development Work\n\n[Poetry][poetry-link] is used to manage the python development environment. \n\nA simple way to create an environment with the desired version of python and poetry is to use [conda][conda-link].  E.g.:\n\n```bash\nconda create -n pybedlite python=3.8 poetry\nconda activate pybedlite\npoetry install\n```\n\nIf the methods listed above do not work try the following:\n```bash\nmamba create -n pybedlite -c conda-forge "python=3.9.16" "poetry=1.6.1"\nmamba activate pybedlite\npoetry install\n```\n\nIf, during `poetry install` on Mac OS X errors are encountered running gcc/clang to build `pybedtools` or other packages with native code, try setting the following and re-running `poetry install`:\n```bash\nexport CFLAGS="-stdlib=libc++"\n``` \n\n[poetry-link]: https://github.com/python-poetry/poetry\n[conda-link]:  https://docs.conda.io/en/latest/miniconda.html\n\n## Checking the Build\n### Run all checks with:\n```bash\n./ci/check.sh\n```\n',
    'author': 'Nils Homer',
    'author_email': 'nils@fulcrumgenomics.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/fulcrumgenomics/pybedlite',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8.0,<4.0.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
