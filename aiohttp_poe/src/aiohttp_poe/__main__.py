from aiohttp_poe.base import run
from aiohttp_poe.samples.echo import EchoBot

if __name__ == "__main__":
    run(EchoBot())
