# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semantix_genai_inference',
 'semantix_genai_inference.inference',
 'semantix_genai_inference.inference.llm']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4,<4.0.0', 'click>=8.1.4,<9.0.0', 'pyyaml>=6.0.1,<7.0.0']

entry_points = \
{'console_scripts': ['semantix-ai = semantix_genai_inference.cli:cli']}

setup_kwargs = {
    'name': 'semantix-genai-inference',
    'version': '0.0.10',
    'description': '',
    'long_description': '# Semantix GenAI Inference\n\nA python client library to help you interact with the Semantix GenAI Inference API.\n\n\n# Installation\n\nIf you\'re using pip, just install it from the latest release:\n\n    $ pip install semantix-genai-inference\n\nElse if you want to run local, clone this repository and install it with poetry:\n\n    $ poetry build\n    $ poetry install\n\n# Usage\n\nTo use it:\n\nFirst, make sure you have a valid API key. You can get one at [Semantix Gen AI Hub](https://home.ml.semantixhub.com/)\n\nSet an environment variable with your api secret:\n\n    $ export SEMANTIX_API_SECRET=<YOUR_API_SECRET>\n    $ semantix-ai --help\n\n## Configuring with semantix.yaml\n\nBefore using the ModelClient, you need to configure the library with a `semantix.yaml` file. This file should be placed in the same directory where your application is executed. The `semantix.yaml` file should contain the necessary API keys and other configuration options for the models you want to use.\n\nHere\'s an example of a `semantix.yaml` file:\n\n```yaml\nproviders:\n  semantixHub:\n    serverId: "YOUR INFERENCE SERVER ID HERE"\n    version: "v0"\n    apiSecret: "YOUR SEMANTIX GEN AI HUB API TOKEN"\n  cohere:\n    apiKey: "YOUR COHERE API KEY"\n    generate:\n      model: "command"\n      version: "v1"\n```\n\nReplace the placeholders with your actual API keys and other configuration options.\n\n## Using ModelClient\n\nThe `ModelClient` class allows you to interact with different models. To create a model client, you need to specify the type of model you want to use. The available options are "alpaca", "llama2", and "cohere".\n\nHere\'s an example of how to create a model client and generate text using the Alpaca model:\n\n```python\nfrom semantix_genai_inference import ModelClient\n\n# Create an Alpaca model client\nclient = ModelClient.create("alpaca")\n\n# Generate text using the Alpaca model\nprompt = "Once upon a time"\ngenerated_text = client.generate(prompt)\nprint(generated_text)\n```\n\nYou can replace "alpaca" with "llama2" or "cohere" to use the Llama2 or Cohere models, respectively.\n\n# DEV - Publish to pypi\n\n    $ poetry config pypi-token.pypi <YOUR_PYPI_TOKEN>\n    $ poetry build\n    $ poetry publish\n\n# DEV - Bump version\n\n    $ poetry version patch | minor | major | premajor | preminor | prepatch | prerelease\n\nSee more at [Poetry version command docs](https://python-poetry.org/docs/cli/#version)\n\n# DEV - Commit message semantics\n\nSee at [Conventional Commits](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)\n',
    'author': 'Dev Team',
    'author_email': 'dev@semantix.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
