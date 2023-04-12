from typing import AsyncIterable

from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from sse_starlette.sse import ServerSentEvent

from fastapi_poe import PoeHandler
from fastapi_poe.types import QueryRequest

template = """PoeBot is an automated version of Edgar Allan Poe.

It can assist with a wide range of tasks, but always responds in the style of Edgar Allan Poe,
and its responses are full of random ghost stories.

{history}
Human: {human_input}
Assistant:"""

prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)


class PoeBotHandler(PoeHandler):
    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        memory = ConversationBufferWindowMemory(k=2)
        for message in query.query[:-1]:
            if message.role == "bot":
                memory.chat_memory.add_ai_message(message.content)
            elif message.role == "user":
                memory.chat_memory.add_user_message(message.content)
        last_message = query.query[-1].content
        chatgpt_chain = LLMChain(
            llm=OpenAI(temperature=0.7), prompt=prompt, verbose=True, memory=memory
        )
        response = await chatgpt_chain.apredict(human_input=last_message)
        yield self.text_event(response)
