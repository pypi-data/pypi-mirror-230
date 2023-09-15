# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['factorlab', 'factorlab.conf']

package_data = \
{'': ['*'], 'factorlab': ['datasets/data/*'], 'factorlab.conf': ['fonts/*']}

install_requires = \
['matplotlib>=3.6.0',
 'numpy>=1.23.3',
 'openpyxl>=3.0.10,<4.0.0',
 'pandas>=1.5.0',
 'plotly>=5.11.0,<6.0.0',
 'seaborn>=0.12.1,<0.13.0',
 'sklearn>=0.0,<0.1',
 'statsmodels>=0.13.2,<0.14.0']

extras_require = \
{':python_version >= "3.9" and python_version < "3.12"': ['scipy>=1.9.1,<2.0.0']}

setup_kwargs = {
    'name': 'factorlab',
    'version': '0.1.2',
    'description': 'Python library which enables the discovery and analysis of alpha and risk factors used in the investment algorithm development process',
    'long_description': '![](factorlab_logo.jpeg)\n\n\n# factorlab\n\nPython library which enables the transformation of raw data into informative alpha and risk factors used in the investment algorithm development process\n\n## Installation\n\n```bash\n$ pip install factorlab\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`factorlab` was created by Systamental. It is licensed under the terms of the Apache License 2.0 license.\n\n## Credits\n\n`factorlab` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Systamental',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
