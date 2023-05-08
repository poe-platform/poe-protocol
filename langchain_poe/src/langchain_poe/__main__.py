import os

from fastapi_poe import run

from .poe import LangChainCatBotHandler

if __name__ == "__main__":
    run(LangChainCatBotHandler(os.environ["OPENAI_API_KEY"]))
