from fastapi_poe import run
from fastapi_poe.samples.catbot import CatBotHandler

if __name__ == "__main__":
    run(CatBotHandler())
