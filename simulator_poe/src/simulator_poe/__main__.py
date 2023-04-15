import os
from simulator_poe import PoeServer

if __name__ == "__main__":
    bot_server = os.environ.get("BOT_SERVER", "127.0.0.1:8080")
    server = PoeServer(bot_server)
    server.start()
