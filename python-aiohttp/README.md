# aiohttp_altai

An implementation of the Poe protocol using aiohttp.

To run it:
- Create a virtual environment (Python 3.9 or higher)
- `pip install .`
- `python -m aiohttp_altai`
- In a different terminal, run [ngrok](https://ngrok.com/) to make it publicly accessible

To include OpenAI's `gpt-3.5-turbo` model in the response
- `export OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY_MhHb9sQe"` before the instructions above
