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
`fastapi_poe.PoeHandler` to make a bot:

```python
from fastapi_poe import PoeHandler, run

class EchoHandler(PoeHandler):
    async def get_response(self, query):
        last_message = query.query[-1].content
        yield self.text_event(last_message)

if __name__ == "__main__":
    run(EchoHandler())
```

For a more advanced example that exercises more of the Poe protocol, see
[Altaibot](./src/fastapi_poe/samples/altai.py).
