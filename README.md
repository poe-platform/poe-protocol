# Poe Bot Protocol

_Note: The Poe Protocol is not live yet. The protocol may still change and it is not yet
possible to create protocol-based bots._

[Poe](https://poe.com) is a platform for interacting with AI-based bots. That includes
well-known chat bots like OpenAI's ChatGPT and Anthropic's Claude, but anyone can create
their own bot by implementing the protocol described in this repository.

## Repo contents

- [Protocol specification](./docs/spec.md)
- [Running a bot](./docs/running-a-bot.md)
- Example implementations
  - [FastAPI](./fastapi_poe/), a simple bot to demonstrate the features of the protocol
  - [aiohttp](./aiohttp_poe/), the same bot built using aiohttp instead of FastAPI
  - [LangChain](./langchain_poe/), an example bot built on top of ChatGPT using
    [LangChain](https://github.com/hwchase17/langchain)
  - [LlamaIndex](./llama_poe/), a knowledge-augmented Poe bot powered by
    [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/) and FastAPI.
  - [Poe Simulator](./simulator_poe/), a simulated Poe server for testing your bot

## Getting started with a sample bot

- Go to
  [the Poe Replit template](https://replit.com/@JelleZijlstra2/Poe-API-Template?v=1)
- Click "Use Template"
- Click "Run" and record the URL where your instance is running. It will be of the form
  "yourproject.yourname.repl.co". Refer to [this screenshot](./docs/images/replit.png)
  if you can't find it. Also record the generated Poe API key, which will be printed to
  the "Console" output.
- Go to the ["Create a bot" form](https://poe.com/create_bot?api=1) on a desktop browser
- Enter your Replit URL and API key
- Create your bot!
- Look at [the catbot explainer](/docs/catbot.md) to play with the sample bot's limited
  capabilities
- Now, extend the [sample code](./fastapi_poe/src/fastapi_poe/samples/) to write your
  own bot to do something new and exciting
- Check out the [spec](/docs/spec.md) to take advantage of all the capabilities of API
  bots

## Writing your own bot

This section provides quick summary links; see ["Running a Bot"](/docs/running-a-bot.md)
for more details.

- To understand what Poe protocol bots can do:
  - Read the [spec](./docs/spec.md)
  - Check out the [simple samples](./fastapi_poe/src/fastapi_poe/samples/)
  - Check out
    [a sample that integrates with ChatGPT](./langchain_poe/src/langchain_poe/poe.py)
  - Check out
    [more samples from LangChain](https://github.com/langchain-ai/langchain-template-poe-fastapi)
  - Check out [more samples from LlamaIndex](https://github.com/run-llama/llama-api)
- To get a bot running locally:
  - `python3 -m pip install fastapi_poe`
  - `python3 -m fastapi_poe`
  - (or use `aiohttp_poe`, or write your own implementation of the spec)
- To connect your bot to Poe:
  - Make it publicly accessible on the Internet (see
    ["Running a Bot"](./docs//running-a-bot.md) for more details), for example:
    - Using [ngrok](https://ngrok.com/) to expose a service running on your machine
    - Using [Replit](https://replit.com/) to run a bot in your browser
    - Using any cloud provider you may have access to
- To create your bot in Poe:
  - ["Create a bot" form](https://poe.com/create_bot?api=1)

## Questions?

Join us on [Discord](https://discord.gg/TKxT6kBpgm) with any questions.
