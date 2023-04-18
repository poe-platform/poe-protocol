# Poe Knowledge Bot with LlamaIndex

A knowledge-augmented Poe bot powered by
[LlamaIndex](https://gpt-index.readthedocs.io/en/latest/) and FastAPI.

Easily ingest and chat with your own data as a knowledge base!

## Quick Start

Follow these steps to quickly setup and run the LlamaIndex bot for Poe:

### Setup Environment

1. Install poetry: `pip install poetry`
2. Install app dependencies: `poetry install`
3. Setup environment variables

| Name             | Required | Description                                                                                                                                                |
| ---------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POE_API_KEY`    | Yes      | This is a secret token that you need to authenticate Poe requests to the API. You can generate this from https://poe.com/create_bot?api=1.                 |
| `OPENAI_API_KEY` | Yes      | This is your OpenAI API key that LlamaIndex needs to call OpenAI services. You can get an API key by creating an account on [OpenAI](https://openai.com/). |

### Run API Server

- Run the API locally: `poetry run start`

```console
INFO:poe_api.llama_handler:Creating new index
INFO:poe_api.llama_handler:Loading data from data/
INFO:llama_index.token_counter.token_counter:> [insert] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [insert] Total embedding token usage: 19274 tokens
2023-04-17 15:24:05,159 - INFO - Application startup complete.
```

- Make the API publicly available with [ngrok](https://ngrok.com/): in a different
  terminal, run `ngrok http 8080`

### Connect Poe to your Bot

- Create your bot at https://poe.com/create_bot?api=1
- Interact with your bot at https://poe.com/

## Test Your LlamaIndex Bot

To quickly verify if your bot is up and running, go to the Swagger UI at
http://localhost:8080/docs, authenticate with your `POE_API_KEY` and issue a query
(satisfying the
[Poe Protocol](https://github.com/poe-platform/poe-protocol/blob/main/docs/spec.md))

Alternatively, to use a sample query, replace `<add your POE_API_KEY here>` in
`Makefile` with your `POE_API_KEY`, then run:

```console
make try
```

## Customize Your LlamaIndex Bot

By default, we ingest documents under `data/` and index them with a
`GPTSimpleVectorIndex`.

You can configure the default behavior via environment variables:

| Name               | Required | Description                                                     |
| ------------------ | -------- | --------------------------------------------------------------- |
| `LLAMA_LOAD_DATA`  | Optional | Whether to ingest documents in `DATA_DIR`.Defaults to `True`    |
| `LLAMA_DATA_DIR`   | Optional | Directory to ingest initial documents from. Defaults to `data/` |
| `LLAMA_INDEX_TYPE` | Optional | Index type (see below for details). Defaults to `simple_dict`   |
| `INDEX_JSON_PATH`  | Optional | Path to saved Index json file. `save/index.json`                |

**Different Index Types** By default, we use a `GPTSimpleVectorIndex` to store document
chunks in memory, and retrieve top-k nodes by embedding similarity. Different index
types are optimized for different data and query use-cases. See this guide on
[How Each Index Works](https://gpt-index.readthedocs.io/en/latest/guides/primer/index_guide.html)
to learn more. You can configure the index type via the `LLAMA_INDEX_TYPE`, see
[here](https://gpt-index.readthedocs.io/en/latest/reference/indices/composability_query.html#gpt_index.data_structs.struct_type.IndexStructType)
for the full list of accepted index type identifiers.

Read more details on [readthedocs](https://gpt-index.readthedocs.io/en/latest/), and
engage with the community on [discord](https://discord.com/invite/dGcwcsnxhU).

## Ingesting Data

LlamaIndex bot for Poe also exposes an API for ingesting additional data by `POST` to
`/add_document` endpoint.

You can use the Swagger UI to quickly experiment with ingesting additional documents:

- Locally: `http://localhost:8080/docs`
- Publiclly via `ngrok`: `https://<instance-id>.ngrok-free.app/docs`
