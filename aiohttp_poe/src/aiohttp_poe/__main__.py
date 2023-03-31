from aiohttp_poe.base import run
from aiohttp_poe.samples.catbot import CatBotHandler

if __name__ == "__main__":
    run(CatBotHandler())
