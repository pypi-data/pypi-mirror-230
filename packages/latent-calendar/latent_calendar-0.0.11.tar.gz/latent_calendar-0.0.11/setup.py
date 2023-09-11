# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['latent_calendar',
 'latent_calendar.datasets',
 'latent_calendar.model',
 'latent_calendar.plot',
 'latent_calendar.plot.core',
 'latent_calendar.segments']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['conjugate-models>=0.1.2,<0.2.0',
 'matplotlib',
 'pandas',
 'pymc>=5.0.0',
 'scikit-learn>=1.0.0']

setup_kwargs = {
    'name': 'latent-calendar',
    'version': '0.0.11',
    'description': 'Analyzing and modeling weekly calendar distributions using latent components',
    'long_description': '# Latent Calendar\n\nAnalyze and model data on a weekly calendar\n\n## Installation\n\nInstall from PyPI: \n\n```bash\npip install latent-calendar\n```\n\nOr install directly from GitHub for the latest functionality. \n\n## Features \n\n- Integrated automatically into `pandas` with `cal` attribute on DataFrames and Series \n- Compatibility with `scikit-learn` pipelines\n- Transform and visualize data on a weekly calendar\n- Model weekly calendar data with a mixture of calendars\n- Create lower dimensional representations of calendar data\n\n\n## Documentation \n\nFind more examples and documentation [here](https://wd60622.github.io/latent-calendar/).',
    'author': 'Will Dean',
    'author_email': 'wd60622@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://wd60622.github.io/latent-calendar/',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
