# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oqtant', 'oqtant.fixtures', 'oqtant.schemas', 'oqtant.util']

package_data = \
{'': ['*']}

install_requires = \
['bert-schemas>=2.0.0,<3.0.0',
 'email-validator>=2.0.0.post2,<3.0.0',
 'fastapi>=0.103.1,<0.104.0',
 'ipyauth>=0.2.6,<0.3.0',
 'ipykernel>=6.23.1,<7.0.0',
 'ipywidgets>=7.6.5,<8.0.0',
 'lmfit>=1.0.3,<2.0.0',
 'matplotlib>=3.6.2,<3.7.0',
 'notebook>=6.4.12,<7.0.0',
 'numpy>=1.23.2,<2.0.0',
 'pydantic-settings>=2.0.3,<3.0.0',
 'pydantic>=2.3.0,<3.0.0',
 'pyjwt[crypto]>=2.6.0,<3.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.21.1,<0.22.0',
 'requests>=2.28.1,<3.0.0',
 'scikit-learn>=1.2.0,<2.0.0',
 'scipy>=1.10.0,<2.0.0',
 'semver>=3.0.0,<4.0.0',
 'tabulate>=0.9.0,<0.10.0',
 'typing-extensions>=4.3.0,<5.0.0',
 'urllib3>=1.26.12,<2.0.0',
 'uvicorn[standard]>=0.20.0,<0.21.0']

entry_points = \
{'console_scripts': ['authorize = '
                     'oqtant.tests.integration.authorize:authorize']}

setup_kwargs = {
    'name': 'oqtant',
    'version': '1.0.0',
    'description': 'Oqtant Desktop Suite',
    'long_description': "# Oqtant\n\n[![License: Apache](https://img.shields.io/badge/License-Apache-yellow.svg)](https://opensource.org/licenses/Apache-2.0)\n[![pypi](https://img.shields.io/pypi/v/oqtant.svg)](https://pypi.python.org/pypi/oqtant)\n[![versions](https://img.shields.io/pypi/pyversions/bert-schemas.svg)](https://pypi.python.org/pypi/bert-schemas)\n[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/Infleqtion.svg?style=social&label=Follow%20%40Infleqtion)](https://twitter.com/Infleqtion)\n\n## 🚀 Quick Install\n\n```python\npip install oqtant\n```\n\n## 🧭 Introduction\n\nThis API contains tools to:\n\n- Access all the functionality of the Oraqle Web App (https://oraqle-dev.infleqtion.com)\n\n  - BARRIER (Barrier Manipulator) jobs\n  - BEC (Ultracold Matter) jobs\n\n- Build parameterized (i.e. optimization) experiments using OqtantJobs\n\n- Submit and retrieve OqtantJob results\n\n## 🤖 How Oqtant Works\n\n- Construct a single or list of jobs using the OqtantJob class\n\n  - 1D parameter sweeps are supported\n\n- Run a single or list of jobs using run_jobs(). The jobs are submitted to run on hardware in FIFO queue.\n\n  - job lists are run sequentially (uninterrupted) unless list exceeds 30 jobs\n\n- As jobs run, OqtantJob objects are created automatically and stored in active_jobs.\n\n  - View these jobs with see_active_jobs()\n  - These jobs are available until the python session ends.\n\n- To operate on jobs from a current or previous session, load them into active_jobs with\n\n  - load_job_from_id(), load_job_from_id_list(), load_job_from_file(), load_job_from_file_list()\n\n- To analyze job objects and use Oqtant's job analysis library, reference the OqtantJob class documentation.\n\nNeed help? Found a bug? Contact <albert@infleqtion.com> for support. Thank you!\n\n## 📓 Documentation\n\n- [Getting started](https://gitlab.com/infleqtion/albert/oqtant/-/blob/main/documentation/INSTALL.md) (installation, setting up the environment, how to run the walkthrough notebooks)\n- [Walkthroughs](https://gitlab.com/infleqtion/albert/oqtant/-/blob/main/documentation/walkthroughs/walkthroughs.md) (demos for creating and submitting jobs)\n- [Oraqle API docs](https://gitlab.com/infleqtion/albert/oqtant/-/blob/main/documentation/oraqle_api_docs.md)\n- [Job Analysis docs](https://gitlab.com/infleqtion/albert/oqtant/-/blob/main/documentation/job_analysis_docs.md)\n",
    'author': 'Larry Buza',
    'author_email': 'lawrence.buza@coldquanta.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://oraqle-dev.infleqtion.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
