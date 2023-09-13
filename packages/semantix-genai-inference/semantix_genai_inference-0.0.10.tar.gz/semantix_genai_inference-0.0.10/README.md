# Semantix GenAI Inference

A python client library to help you interact with the Semantix GenAI Inference API.


# Installation

If you're using pip, just install it from the latest release:

    $ pip install semantix-genai-inference

Else if you want to run local, clone this repository and install it with poetry:

    $ poetry build
    $ poetry install

# Usage

To use it:

First, make sure you have a valid API key. You can get one at [Semantix Gen AI Hub](https://home.ml.semantixhub.com/)

Set an environment variable with your api secret:

    $ export SEMANTIX_API_SECRET=<YOUR_API_SECRET>
    $ semantix-ai --help

## Configuring with semantix.yaml

Before using the ModelClient, you need to configure the library with a `semantix.yaml` file. This file should be placed in the same directory where your application is executed. The `semantix.yaml` file should contain the necessary API keys and other configuration options for the models you want to use.

Here's an example of a `semantix.yaml` file:

```yaml
providers:
  semantixHub:
    serverId: "YOUR INFERENCE SERVER ID HERE"
    version: "v0"
    apiSecret: "YOUR SEMANTIX GEN AI HUB API TOKEN"
  cohere:
    apiKey: "YOUR COHERE API KEY"
    generate:
      model: "command"
      version: "v1"
```

Replace the placeholders with your actual API keys and other configuration options.

## Using ModelClient

The `ModelClient` class allows you to interact with different models. To create a model client, you need to specify the type of model you want to use. The available options are "alpaca", "llama2", and "cohere".

Here's an example of how to create a model client and generate text using the Alpaca model:

```python
from semantix_genai_inference import ModelClient

# Create an Alpaca model client
client = ModelClient.create("alpaca")

# Generate text using the Alpaca model
prompt = "Once upon a time"
generated_text = client.generate(prompt)
print(generated_text)
```

You can replace "alpaca" with "llama2" or "cohere" to use the Llama2 or Cohere models, respectively.

# DEV - Publish to pypi

    $ poetry config pypi-token.pypi <YOUR_PYPI_TOKEN>
    $ poetry build
    $ poetry publish

# DEV - Bump version

    $ poetry version patch | minor | major | premajor | preminor | prepatch | prerelease

See more at [Poetry version command docs](https://python-poetry.org/docs/cli/#version)

# DEV - Commit message semantics

See at [Conventional Commits](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)
