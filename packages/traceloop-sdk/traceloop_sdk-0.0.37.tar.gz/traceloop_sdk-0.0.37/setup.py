# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sdk', 'sdk.decorators', 'sdk.semconv', 'sdk.tracing', 'sdk.utils']

package_data = \
{'': ['*']}

install_requires = \
['opentelemetry-api>=1.19.0,<2.0.0',
 'opentelemetry-exporter-otlp-proto-http>=1.19.0,<2.0.0',
 'opentelemetry-instrumentation-openai>=0.0.3,<0.0.4',
 'opentelemetry-instrumentation-pinecone>=0.0.2,<0.0.3',
 'opentelemetry-instrumentation-pymysql>=0.40b0,<0.41',
 'opentelemetry-instrumentation-requests>=0.40b0,<0.41',
 'opentelemetry-instrumentation-urllib3>=0.40b0,<0.41',
 'opentelemetry-sdk>=1.19.0,<2.0.0']

setup_kwargs = {
    'name': 'traceloop-sdk',
    'version': '0.0.37',
    'description': 'Traceloop Software Development Kit (SDK) for Python',
    'long_description': '# traceloop-sdk\n\nProject description here.\n',
    'author': 'Gal Kleinman',
    'author_email': 'gal@traceloop.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<3.12',
}


setup(**setup_kwargs)
