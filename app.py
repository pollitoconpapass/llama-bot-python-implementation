import chainlit as cl
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable.config import RunnableConfig


model = Ollama(model="llama3.2:1b",)

@cl.on_chat_start
async def on_chat_start():
    msg = cl.Message(content="xxx")  # -> to initialize it
    await msg.send()

    msg.content = "Hello, how can I help you?"
    await msg.update()

    cl.user_session.set("message_history", [])


@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    message_history = message_history[-10:] # -> to limit the history

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You're a helpful AI assistant. You can answer whatever question the user asks you.
                Use the message history: "{message_history}" to mantain the context of the conversation, 
                answer in a simple and understandable way. Give the 'content' field as answer. Do NOT 
                include brackets in your responses.""",
            ),
            ("human", "{role}: {question}")
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

    runnable = cl.user_session.get("runnable")
    msg = cl.Message(content="")

    for chunk in await cl.make_async(runnable.stream)(
        {"role": "human", "question": message.content, "message_history": message_history},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()

    message_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("message_history", message_history)
