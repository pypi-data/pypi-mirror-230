# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sdk', 'sdk.decorators', 'sdk.tracing', 'sdk.utils']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.6,<0.5.0',
 'opentelemetry-api>=1.19.0,<2.0.0',
 'opentelemetry-exporter-otlp-proto-http>=1.19.0,<2.0.0',
 'opentelemetry-instrumentation-haystack>=0.0.1,<0.0.2',
 'opentelemetry-instrumentation-openai>=0.0.5,<0.0.6',
 'opentelemetry-instrumentation-pinecone>=0.0.2,<0.0.3',
 'opentelemetry-instrumentation-pymysql>=0.40b0,<0.41',
 'opentelemetry-instrumentation-requests>=0.40b0,<0.41',
 'opentelemetry-instrumentation-urllib3>=0.40b0,<0.41',
 'opentelemetry-sdk>=1.19.0,<2.0.0',
 'opentelemetry-semantic-conventions-ai>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'traceloop-sdk',
    'version': '0.0.43b4',
    'description': 'Traceloop Software Development Kit (SDK) for Python',
    'long_description': '# traceloop-sdk\n\nTraceloop’s Python SDK allows you to easily start monitoring and debugging your LLM execution. Tracing is done in a non-intrusive way, built on top of OpenTelemetry. You can choose to export the traces to Traceloop, or to your existing observability stack.\n\n```python\nTraceloop.init(app_name="joke_generation_service")\n\n@workflow(name="joke_creation")\ndef create_joke():\n    completion = openai.ChatCompletion.create(\n        model="gpt-3.5-turbo",\n        messages=[{"role": "user", "content": "Tell me a joke about opentelemetry"}],\n    )\n\n    return completion.choices[0].message.content\n```\n',
    'author': 'Gal Kleinman',
    'author_email': 'gal@traceloop.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/traceloop/openllmetry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<3.12',
}


setup(**setup_kwargs)
