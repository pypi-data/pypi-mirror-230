# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taos', 'taosrest']

package_data = \
{'': ['*']}

install_requires = \
['iso8601==1.0.2', 'pytest-cov>=4.0.0,<5.0.0', 'pytz', 'requests>=2.27.1']

extras_require = \
{'ws:python_version >= "3.7" and python_version < "4.0"': ['taos-ws-py>=0.2.0']}

entry_points = \
{'sqlalchemy.dialects': ['taos = taos.sqlalchemy:TaosDialect',
                         'taosrest = taosrest.sqlalchemy:TaosRestDialect',
                         'taosws = taos.sqlalchemy:TaosWsDialect']}

setup_kwargs = {
    'name': 'taospy',
    'version': '2.7.12',
    'description': 'TDengine connector for python',
    'long_description': '# TDengine Connector for Python\n\n| Github Workflow | PyPI Version | PyPI Downloads | CodeCov |\n| --------------- | ------------ | -------------- | ------- |\n| ![workflow](https://img.shields.io/github/actions/workflow/status/taosdata/taos-connector-python/test.yml) | ![PyPI](https://img.shields.io/pypi/v/taospy) | ![PyPI](https://img.shields.io/pypi/dm/taospy) | [![codecov](https://codecov.io/gh/taosdata/taos-connector-python/branch/main/graph/badge.svg?token=BDANN3DBXS)](https://codecov.io/gh/taosdata/taos-connector-python) |\n\n\n\n\n[TDengine](https://github.com/taosdata/TDengine) connector for Python enables python programs to access TDengine, using\nan API which is compliant with the Python DB API 2.0 (PEP-249). It contains two modules:\n\n1. The `taos` module. It uses TDengine C client library for client server communications.\n2. The `taosrest` module. It wraps TDengine RESTful API to Python DB API 2.0 (PEP-249). With this module, you do not need to install the TDengine C client library.\n\n## Install taospy\n\nYou can use `pip` to install the connector from PyPI:\n\n```bash\npip install taospy\n```\n\nOr with git url:\n\n```bash\npip install git+https://github.com/taosdata/taos-connector-python.git\n```\n\nNote: taospy v2.7.2 requirs Python 3.6+. The early versions of taospy from v2.5.0 to v2.7.1 require Python 3.7+.\n\n## Install taos-ws-py\n\n### Install with taospy\n\n```bash\npip install taospy[ws]\n```\n\n### Install taos-ws-py only\n\n```bash\npip install taos-ws-py\n```\n\nNote: The taosws module is provided by taos-ws-py package separately from v2.7.2. It is part of early version of taospy.\ntaos-ws-py requires Python 3.7+.\n\n## Docs\n\n[Reference](https://docs.tdengine.com/reference/connector/python/)\n\n## Limitation\n\n- `taosrest` is designed to use with taosAdapter. If your TDengine version is older than v2.4.0.0, taosAdapter may not\n  be available.\n\n## License\n\nWe use MIT license for Python connector.\n',
    'author': 'Taosdata Inc.',
    'author_email': 'support@taosdata.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
