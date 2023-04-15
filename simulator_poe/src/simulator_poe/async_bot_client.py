
from aiohttp import ClientSession
from aiohttp_sse_client2 import client
from fastapi.encoders import jsonable_encoder
from simulator_poe.poe_messages import ProtocolMessage, QueryRequest

import os  # noqa: F401
import time

_USER_ID = 0
_API_VERSION = "1.0"


class AsyncBotClient:
    def __init__(self, end_point):
        self.end_point = end_point
        self.session = None
        self.headers = {"Authorization": "bearer {os.environ.get('POE_API_KEY', '')}"}
        self.conversation_id = "c-1234567"
        self.msg_id = 0

    def build_single_Message(self, role, msg):
        ret = ProtocolMessage(
            role=role,
            content=msg,
            content_type="text/plain",
            timestamp=round(time.time()*1000000),
            message_id=f"m-{self.msg_id}",
            message_type=None,
            feedback=[])
        self.msg_id += 1
        return ret

    def build_query_Message(self, msg, context):
        protocol_msg = self.build_single_Message("user", msg)
        context.messages.append(protocol_msg)

        ret = QueryRequest(
            version=_API_VERSION,
            type="query",
            user_id=_USER_ID,
            conversation_id=self.conversation_id,
            message_id=f"m-{self.msg_id}",
            query=context.messages)
        return jsonable_encoder(ret)

    def on_error(self):
        print("Error streaming events")
        raise RuntimeError("Error streaming events")

    async def stream_request(self, msg, context, debug=False):
        event_count = 0
        if self.session is None:
            self.session = ClientSession()
        body = self.build_query_Message(msg, context)
        if debug:
            print(f"Sending to the bot server: {body}")
        async with client.EventSource(
            f"http://{self.end_point}",
            option={"method": "POST"},
            session=self.session,
            headers=self.headers,
            json=body,
            on_error=self.on_error,
        ) as event_source:
            try:
                async for event in event_source:
                    event_count += 1
                    yield event
            except ConnectionError:
                print("Connection error")
