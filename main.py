# Welcome to the Poe API tutorial. The starter code provided provides you with a quick way to get
# a bot running. By default, the starter code uses the EchoBot, which is a simple bot that echos
# a message back at its user and is a good starting point for your bot, but you can
# comment/uncomment any of the following code to try out other example bots.

from fastapi_poe import make_app
from fastapi_poe.samples.concurrent_battle import ConcurrentBattleBot

bot = ConcurrentBattleBot()

app = make_app(bot, allow_without_key=True)
