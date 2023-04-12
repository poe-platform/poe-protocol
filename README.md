# Poe Bot Protocol

_Note: The Poe Protocol is not live yet. The protocol may still change and it is not yet
possible to create protocol-based bots._

[Poe](https://poe.com) is a platform for interacting with AI-based bots. That includes
well-known chat bots like OpenAI's ChatGPT and Anthropic's Claude, but anyone can create
their own bot by implementing the protocol described in this repository.

## Repo contents

- [Protocol specification](./docs/spec.md)
- Example implementations
  - [FastAPI](./fastapi_poe/), a simple bot to demonstrate the features of the protocol
  - [aiohttp](./aiohttp_poe/), the same bot built using aiohttp instead of FastAPI
  - [LangChain](./langchain_poe/), an example bot built on top of ChatGPT using
    [LangChain](https://github.com/hwchase17/langchain)

## Getting started

- Install [ngrok](https://ngrok.com/) and Python 3.7+
- `python3 -m pip install fastapi_poe`
- `python3 -m fastapi_poe`
- `ngrok http 8080`
- Go to https://poe.com/create_bot?api=1
- Enter your ngrok URL
- Create your bot!
- Look at [the catbot explainer](/docs/catbot.md) to play with the sample bot's limited
  capabilities
- Now, extend the [sample code](./fastapi_poe/src/fastapi_poe/samples/) to write your
  own bot to do something new and exciting
- Check out the [spec](/docs/spec.md) to take advantage of all the capabilities of API
  bots
