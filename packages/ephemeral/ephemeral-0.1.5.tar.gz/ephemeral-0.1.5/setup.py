# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ephemeral']

package_data = \
{'': ['*'],
 'ephemeral': ['static/main.css',
               'static/node_modules/normalize.css/normalize.css',
               'templates/*']}

install_requires = \
['Flask>=2.3,<3.0',
 'cryptography>=41.0.3,<42.0.0',
 'gunicorn>=21.2,<22.0',
 'redis>=5.0,<6.0']

scripts = \
['ephemeral.sh']

setup_kwargs = {
    'name': 'ephemeral',
    'version': '0.1.5',
    'description': 'Self-destructing messages',
    'long_description': '# ephemeral - Self-destructing messages\n\nEphemeral is a web application for sharing short messages. Messages can be opened\nonly once, giving an instant feedback to recipient on whether the message was\ncompromised(read by someone else) or not. This makes the app a reasonably secure,\nand convenient way to share secrets.\n\n## Highlights\n\n- Simple, easy-to-audit code\n- Messages are encrypted at rest\n\n\n## Installing\n\n```sh\npip install ephemeral\n```\n\nAfter installation you can use the `ephemeral.sh` command to start the\napplication (see below).\n\n\n## Running\n\nAlways put this application behind an HTTPS-terminating reverse proxy when exposing to\npublic networks!\n\nEphemeral uses Redis as the data store. Assuming Redis is running on `localhost`,\n\n```sh\nEPHEMERAL_REDIS_HOST=localhost EPHEMERAL_SECRET_KEY=hunter2 ephemeral.sh 0.0.0.0:8080\n```\n\nwill start the application listning on port 8080 on all network interfaces.\n\nPoint your browser at http://localhost:8080/add to add a message.\n\n\n## Developing\n\nPrerequisites:\n\n- Python 3\n- Poetry\n\nInitialize a virtualenv with dev dependencies installed:\n\n```sh\nmake develop\n```\n\n\n### Running unit-tests\n\n```sh\nmake test\n```\n\n\n### Starting a development instance of the application\n\nStart the application in development mode with debugging enabled:\n\n```sh\nmake dev-server\n```\n\n\n### Starting/stopping a development Docker stack\n\nThe development Docker (Compose) stack includes Redis container and an application\ncontainer built from source.\n\nPrerequisites:\n\n- Docker\n- docker-compose\n\n```sh\nmake clean build\n\nmake container-image\n\nmake compose-up\n\nmake compose-ps\n```\n\nStop and destroy running stack:\n\n```sh\nmake compose-down\n```\n\n\n### Running E2E tests\n\nStart a stack and run Behave tests against it:\n\n```sh\nmake compose-up\n\nmake e2e-test\n```\n',
    'author': 'Sergej Alikov',
    'author_email': 'sergej@alikov.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/node13h/ephemeral',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'scripts': scripts,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
