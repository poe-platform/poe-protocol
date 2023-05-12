# fastapi_poe

An implementation of the Poe protocol using FastAPI.

To run it:

- Create a virtual environment (Python 3.7 or higher)
- `pip install .`
- `python -m fastapi_poe`
- In a different terminal, run [ngrok](https://ngrok.com/) to make it publicly
  accessible

## Write your own bot

This package can also be used as a base to write your own bot. You can inherit from
`fastapi_poe.PoeBot` to make a bot:

```python
from fastapi_poe import PoeBot, run

class EchoBot(PoeBot):
    async def get_response(self, query):
        last_message = query.query[-1].content
        yield self.text_event(last_message)

if __name__ == "__main__":
    run(EchoBot())
```

## Enable authentication

Poe servers send requests containing Authorization HTTP header in the format "Bearer
<api_key>," where api_key is the API key configured in the bot settings. \

To validate the requests are from Poe Servers, you can either set the environment
variable POE_API_KEY or pass the parameter api_key in the run function like:

```python
if __name__ == "__main__":
    run(EchoBot(), api_key=<key>)
```
