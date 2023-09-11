# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lmu_meteo_api']

package_data = \
{'': ['*']}

install_requires = \
['ipykernel>=6.25.2,<7.0.0',
 'ipython>=8.15.0,<9.0.0',
 'matplotlib>=3.7.2,<4.0.0',
 'numpy>=1.25.2,<2.0.0',
 'pandas>=2.1.0,<3.0.0',
 'pytest>=7.4.2,<8.0.0',
 'requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'lmu-meteo-api',
    'version': '0.2.0',
    'description': 'Python interface to request data from the LMU Meteorology station.',
    'long_description': '# LMU Meteo Data API\n\nThe LMU provides free high-quality meteodata through a web API, that can be accessed without authentification. This package should help to acess the API and return the data as dataframe.<br>\nThe package is published on PyPi for easy installation using pip.\n\n## API documentation\n<url>https://www.meteo.physik.uni-muenchen.de/request-beta/</url>\n\n## How to install\n\n```\npip install lmu_meteo_api\n```\n\n## For developers\n\nSet up you virtual environment\n```bash\npython3.10 -m venv .venv\n```\n\nInstall dependencies\n```bash\npoetry install\n```\n\n(Optional) Publish new package\n```bash\npoetry build\npoetry publish\n```',
    'author': 'DanielKuebi',
    'author_email': 'daniflug95@live.at',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
