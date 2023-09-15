# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['werkit',
 'werkit.aws_lambda',
 'werkit.common',
 'werkit.compute',
 'werkit.compute.destination',
 'werkit.compute.graph',
 'werkit.orchestrator',
 'werkit.orchestrator.orchestrator_lambda',
 'werkit.orchestrator.testing',
 'werkit.orchestrator.testing.worker_service',
 'werkit.scripts']

package_data = \
{'': ['*'],
 'werkit.compute': ['generated/*'],
 'werkit.compute.graph': ['generated/*'],
 'werkit.orchestrator.orchestrator_lambda': ['generated/*'],
 'werkit.orchestrator.testing.worker_service': ['generated/*']}

install_requires = \
['jsonschema>=4.1.2,<5.0.0', 'missouri==0.3.0', 'semver==3.0.1']

extras_require = \
{'aws-lambda-build': ['executor>=21.0'],
 'cli': ['click>=8.0.3,<9.0.0'],
 'client': ['boto3==1.20.32'],
 'compute-graph': ['artifax==0.5'],
 'compute-graph:python_version < "3.10"': ['typing-extensions>=4'],
 'lambda-common': ['harrison>=2.0,<3.0'],
 'rds-graphile-worker': ['rds-graphile-worker-client>=0.1.1,<0.2.0']}

setup_kwargs = {
    'name': 'werkit',
    'version': '0.35.1',
    'description': 'Toolkit for encapsulating Python-based computation into deployable and distributable tasks',
    'long_description': 'None',
    'author': 'Paul Melnikow',
    'author_email': 'github@paulmelnikow.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/metabolize/werkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
