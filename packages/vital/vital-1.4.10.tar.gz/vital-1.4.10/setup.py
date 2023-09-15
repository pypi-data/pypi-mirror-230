# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vital', 'vital.api', 'vital.api.schema', 'vital.internal']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.0.1,<3.0.0',
 'arrow',
 'importlib-metadata>=3.7.3,<4.0.0',
 'pydantic>=1.10.7,<2.0.0',
 'requests',
 'svix>=0.41.2,<0.42.0',
 'typed-ast>=1.5.4,<2.0.0']

setup_kwargs = {
    'name': 'vital',
    'version': '1.4.10',
    'description': '',
    'long_description': "# vital-python\n\nThe official Python Library for [Vital API](https://docs.tryvital.io)\n\n# Install\n\n```\npip install vital\n```\n\n# Installing locally\n\n```\npoetry build --format sdist\ntar -xvf dist/*-`poetry version -s`.tar.gz -O '*/setup.py' > setup.py\n```\n\n## Documentation\n\nPlease refer to the official [Vital docs](https://docs.tryvital.io) provide a full reference on using this library.\n",
    'author': 'maitham',
    'author_email': 'maitham@tryvital.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/adeptlabs/vital-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
