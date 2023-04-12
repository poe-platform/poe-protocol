from fastapi_poe import run

from .poe import PoeBotHandler

if __name__ == "__main__":
    run(PoeBotHandler())
