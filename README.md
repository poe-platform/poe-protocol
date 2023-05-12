# Poe Bot Protocol

_Note: The Poe Protocol is not live yet. The protocol may still change and it is not yet
possible to create protocol-based bots._

[Poe](https://poe.com) is a platform for interacting with AI-based bots. That includes
well-known chat bots like OpenAI's ChatGPT and Anthropic's Claude, but anyone can create
their own bot by implementing the protocol described in this repository.

## Contents

- Specifications: Check out the [specs document](./spec.md) to understand the full
  capabilities of the protocol.
- Quick Start: Checkout our
  [API Bots tutorial](https://github.com/poe-platform/api-bot-tutorial) which includes
  starter code and instructions to help you get your bot running.
- Example implementations
  - [HerokuCat](https://poe.com/HerokuCat), a demo bot to demonstrate the features of
    the protocol.
    - See the
      [documentation](https://github.com/poe-platform/api-bot-tutorial/blob/main/catbot/catbot.md)
      for a full list of commands supported.
    - The source code for this bot is available in the
      [tutorial](https://github.com/poe-platform/api-bot-tutorial/blob/main/catbot.py).
  - [fastapi-poe](./fastapi_poe/), a library for building Poe bots using the FastAPI
    framework. We recommend using this library if you are building your own bot.
  - [aiohttp-poe](./aiohttp_poe/), a similar library built on top of aiohttp
  - [langchain-poe](./langchain_poe/), an example bot built on top of ChatGPT using
    [LangChain](https://github.com/hwchase17/langchain)
  - [llama-poe](./llama_poe/), a knowledge-augmented Poe bot powered by
    [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/) and FastAPI.
  - [Poe Simulator](./simulator_poe/), a simulated Poe server for testing your bot

## Questions?

Join us on [Discord](https://discord.gg/TKxT6kBpgm) with any questions.
