# aiohttp_poe

An implementation of the Poe protocol using aiohttp.

To run it:

- Create a virtual environment (Python 3.7 or higher)
- `pip install .`
- `python -m aiohttp_poe`
- In a different terminal, run [ngrok](https://ngrok.com/) to make it publicly
  accessible

## Write your own bot

This package can also be used as a base to write your own bot. You can inherit from
`aiohttp_poe.PoeHandler` to make a bot:

```python
from aiohttp_poe import PoeHandler, run

class EchoHandler(PoeHandler):
    async def get_response(self, query, request):
        last_message = query["query"][-1]["content"]
        yield self.text_event(last_message)


if __name__ == "__main__":
    run(EchoHandler())
```

## Enable authentication

Poe servers send requests containing Authorization HTTP header in the format "Bearer
<api_key>," where api_key is the API key configured in the bot settings. \

To validate the requests are from Poe Servers, you can either set the environment
variable POE_API_KEY or pass the parameter api_key in the run function like:

```python
if __name__ == "__main__":
    run(EchoHandler(), api_key=<key>)
```

For a more advanced example that exercises more of the Poe protocol, see
[Catbot](./src/aiohttp_poe/samples/catbot.py).
