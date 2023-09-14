import os
from typing import Callable, List, Optional, Union

from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from glow.llm.chains import CommandLineChain, read_system_info
from glow.constants import GLOW_ENV_FILE
from glow.colors import cprint
from glow.utils.dotenv import load_dot_env_file


def build_openai_llm(**kwargs) -> Optional[ChatOpenAI]:
    load_dot_env_file(GLOW_ENV_FILE)

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if OPENAI_API_KEY is None:
        cprint(f"🔑 OPENAI_API_KEY is not set in environment file: {GLOW_ENV_FILE}", ["red"])
        return

    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, **kwargs)
    return llm


def build_command_suggest(**kwargs) -> Optional[Callable]:
    """
    **kwargs are the kwargs to start a ChatOpenAI
    like:
    - model

    This function will return a function that can suggest command
    """
    llm = build_openai_llm(**kwargs)
    if llm is None:
        return
    chain = CommandLineChain.from_llm(llm=llm, verbose=False)
    system_info = read_system_info()

    def command_suggest(question: str) -> str:
        suggest = chain.run(question=question, system=system_info)
        if "🍔🍔🍔" not in suggest:
            return suggest
        if "🍟🍟🍟" not in suggest:
            return suggest

        suggest = suggest.split("🍔🍔🍔")[1]
        suggest = suggest.split("🍟🍟🍟")[0]
        return suggest

    return command_suggest


def build_llm_ask(**kwargs) -> Optional[Callable]:
    kwargs.update(
        {
            "streaming": True,
            "callbacks": [
                StreamingStdOutCallbackHandler(),
            ],
        }
    )
    llm = build_openai_llm(**kwargs)
    if llm is None:
        return

    def ask(question: str, system_content: Optional[str] = None) -> Optional[str]:
        messages: List[BaseMessage] = [
            HumanMessage(content=question),
        ]
        if system_content is not None:
            messages.insert(
                0,
                SystemMessage(
                    content=system_content,
                ),
            )
        print("=" * 30)
        llm(messages=messages)
        print("\n")
        print("=" * 30)

    return ask
