import asyncio
import dataclasses
import json
from typing import List

from prompt_toolkit import HTML, print_formatted_text, prompt
from prompt_toolkit.styles import Style

from simulator_poe.async_bot_client import AsyncBotClient
from simulator_poe.poe_messages import ProtocolMessage


@dataclasses.dataclass
class ServerContext:
    """The context of the server. This is the state of the conversation."""

    messages: List[ProtocolMessage]


style = Style.from_dict(
    {"poe": "#5d5cde", "bot": "#af875f", "info": "#008000", "error": "#ff0000"}
)


class PoeServer:
    """The Poe server simulator. This is the server that the bot connects to."""

    def __init__(self, bot_server):
        self.context = ServerContext(messages=[])
        self.bot_client = AsyncBotClient(bot_server)
        self.debug = False

    def print_usage(self):
        print_formatted_text(HTML("Welcome to the Poe server simulator!"))
        print_formatted_text(HTML("!q -- quit Poe server simulator"))
        print_formatted_text(HTML("!c -- clear the context"))
        print_formatted_text(HTML("!d -- toggle debug mode"))

    def start(self):
        self.print_usage()

        while True:
            answer = prompt(HTML("<poe>Poe server &gt;</poe> "), style=style)
            if answer == "!q":
                if self.bot_client and self.bot_client.session:
                    asyncio.get_event_loop().run_until_complete(
                        self.bot_client.session.close()
                    )
                return
            elif answer == "!c":
                self.context.messages = []
                print_formatted_text(HTML("<info>Context cleared</info>"), style=style)
                continue
            elif answer == "!d":
                self.debug = not self.debug
                print_formatted_text(
                    HTML(f"<info>Debug set to {self.debug}</info>"), style=style
                )
                continue
            print_formatted_text()
            asyncio.get_event_loop().run_until_complete(self.send_message(answer))
            print_formatted_text()

    async def send_message(self, msg: str):
        print_formatted_text(HTML("<bot>Bot server &gt;</bot> "), end="", style=style)
        content = ""
        async for event in self.bot_client.stream_request(
            msg, self.context, debug=self.debug
        ):
            if event.message == "text":
                text_data = json.loads(event.data)
                content += text_data["text"]
                print(text_data["text"])
            elif event.message == "done":
                self.context.messages.append(
                    self.bot_client.build_single_Message("bot", content)
                )
                return
