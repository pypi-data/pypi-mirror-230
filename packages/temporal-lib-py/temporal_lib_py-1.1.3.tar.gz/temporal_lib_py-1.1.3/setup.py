# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['temporallib',
 'temporallib.auth',
 'temporallib.client',
 'temporallib.encryption',
 'temporallib.worker']

package_data = \
{'': ['*']}

install_requires = \
['google-auth>=2.19.1,<3.0.0',
 'macaroonbakery>=1.3.1,<2.0.0',
 'pycryptodome>=3.15.0,<4.0.0',
 'sentry-sdk>=1.29.2,<2.0.0',
 'temporalio>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'temporal-lib-py',
    'version': '1.1.3',
    'description': 'A wrapper library for candid-based temporal authentication',
    'long_description': '# temporal-lib-py\n\nThis library provides a partial wrapper for the _Client.connect_ method from\n[temporalio/sdk-python](https://github.com/temporalio/sdk-python/tree/main/temporalio)\nby adding candid-based authentication, Google IAM-based authentication and\nencryption. It also provides a partial wrapper for the Temporal Worker by adding\na Sentry interceptor which can be enabled through config.\n\n## Building\n\nThis library uses [poetry](https://github.com/python-poetry/poetry) for\npackaging and managing dependencies. To build the wheel file simply run:\n\n```bash\npoetry build -f wheel\n```\n\n## Usage\n\n### Client\n\nThe following code shows how a client connection is created by using the\noriginal (vanilla) temporalio sdk:\n\n```python\nfrom temporalio.client import Client\nasync def main():\n    client = await Client.connect("localhost:7233")\n    ...\n```\n\nIn order to add authorization and encryption capabilities to this client we\nreplace the connect call as follows:\n\n#### Candid-based authorization\n\n```python\nfrom temporallib.client import Client, Options\nfrom temporallib.auth import AuthOptions, MacaroonAuthOptions, KeyPair\nfrom temporallib.encryption import EncryptionOptions\nasync def main():\n    # alternatively options could be loaded from a yaml file as the one showed below\n    cfg = Options(\n        host="localhost:7233",\n        auth=AuthOptions(provider="candid", config=MacaroonAuthOptions(keys=KeyPair(...))),\n        encryption=EncryptionOptions(key="key")\n        ...\n    )\n    client = await Client.connect(cfg)\n\t...\n```\n\nThe structure of the YAML file which can be used to construct the Options is as\nfollows:\n\n```yaml\nhost: "localhost:7233"\nqueue: "test-queue"\nnamespace: "test"\nencryption:\n  key: "HLCeMJLLiyLrUOukdThNgRfyraIXZk918rtp5VX/uwI="\nauth:\n  provider: "candid"\n  config:\n    macaroon_url: "http://localhost:7888/macaroon"\n    username: "test"\n    keys:\n      private: "MTIzNDU2NzgxMjM0NTY3ODEyMzQ1Njc4MTIzNDU2Nzg="\n      public: "ODc2NTQzMjE4NzY1NDMyMTg3NjU0MzIxODc2NTQzMjE="\ntls_root_cas: |\n  \'base64 certificate\'\n```\n\n#### Google IAM-based authorization\n\n```python\nfrom temporallib.client import Client, Options\nfrom temporallib.auth import AuthOptions, GoogleAuthOptions\nfrom temporallib.encryption import EncryptionOptions\nasync def main():\n    # alternatively options could be loaded from a yaml file as the one showed below\n    cfg = Options(\n        host="localhost:7233",\n        auth=AuthOptions(provider="google", config=GoogleAuthOptions(private_key=...)),\n        encryption=EncryptionOptions(key="key")\n        ...\n    )\n    client = await Client.connect(cfg)\n\t...\n```\n\nThe structure of the YAML file which can be used to construct the Options is as\nfollows:\n\n```yaml\nhost: "localhost:7233"\nqueue: "test-queue"\nnamespace: "test"\nencryption:\n  key: "HLCeMJLLiyLrUOukdThNgRfyraIXZk918rtp5VX/uwI="\nauth:\n  provider: "google"\n  config:\n    type: "service_account"\n    project_id: "REPLACE_WITH_PROJECT_ID"\n    private_key_id: "REPLACE_WITH_PRIVATE_KEY_ID"\n    private_key: "REPLACE_WITH_PRIVATE_KEY"\n    client_email: "REPLACE_WITH_CLIENT_EMAIL"\n    client_id: "REPLACE_WITH_CLIENT_ID"\n    auth_uri: "https://accounts.google.com/o/oauth2/auth"\n    token_uri: "https://oauth2.googleapis.com/token"\n    auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"\n    client_x509_cert_url: "REPLACE_WITH_CLIENT_CERT_URL"\ntls_root_cas: |\n  \'base64 certificate\'\n```\n\n### Worker\n\nThe following code shows how a Worker is created by using the original (vanilla)\ntemporalio sdk:\n\n```python\nfrom temporalio.worker import Worker\nfrom temporalio.client import Client\nasync def main():\n    client = await Client.connect("localhost:7233")\n    worker = Worker(\n        client,\n        task_queue=task_queue,\n        workflows=workflows,\n        activities=activities,\n    )\n    await worker.run()\n    ...\n```\n\nIn order to add Sentry logging capabilities to this worker we replace the worker\ninitialization as follows:\n\n```python\nfrom temporallib.worker import Worker, WorkerOptions, SentryOptions\nfrom temporallib.client import Client\n\nclient = await Client.connect(cfg)\nworker = Worker(\n    client,\n    task_queue=task_queue,\n    workflows=workflows,\n    activities=activities,\n    worker_opt=WorkerOptions(sentry=SentryOptions(dsn="dsn", release="release", environment="environment", redact_params=True)),\n)\nawait worker.run()\n\n```\n\nNote that you can optionally enable parameter redaction to hide event parameters\nthat are sent to Sentry.\n\n## Samples\n\nMore examples of workflows using this library can be found here:\n\n- [temporal-lib-samples](https://github.com/canonical/temporal-lib-samples)\n',
    'author': 'gtato',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
