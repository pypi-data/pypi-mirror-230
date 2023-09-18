# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chalicelib_smaht',
 'chalicelib_smaht.checks',
 'chalicelib_smaht.checks.helpers',
 'chalicelib_smaht.scripts']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2==2.10.1',
 'MarkupSafe==1.1.1',
 'PyJWT>=2.5.0,<3.0.0',
 'cgap-pipeline-utils==23.0',
 'click>=7.1.2,<8.0.0',
 'dcicutils>=7.5.1,<8.0.0',
 'elasticsearch-dsl>=7.0.0,<8.0.0',
 'elasticsearch>=7.13.4,<8.0.0',
 'foursight-core==4.4.0.1b34',
 'geocoder==1.38.1',
 'gitpython>=3.1.2,<4.0.0',
 'google-api-python-client>=1.12.5,<2.0.0',
 'magma-suite>=1.2.2,<2.0.0',
 'pytest==5.1.2',
 'pytz>=2020.1,<2021.0',
 'tibanna-ff>=1.3.0,<2.0.0']

entry_points = \
{'console_scripts': ['local-check-execution = '
                     'chalicelib_smaht.scripts.local_check_execution:main',
                     'publish-to-pypi = '
                     'dcicutils.scripts.publish_to_pypi:main']}

setup_kwargs = {
    'name': 'foursight-smaht',
    'version': '0.0.1.1b26',
    'description': 'Serverless Chalice Application for Monitoring',
    'long_description': 'None',
    'author': '4DN-DCIC Team',
    'author_email': 'support@4dnucleome.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.8',
}


setup(**setup_kwargs)
