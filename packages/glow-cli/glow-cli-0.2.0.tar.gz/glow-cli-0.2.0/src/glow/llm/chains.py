import subprocess

from langchain.chains import LLMChain
from langchain import PromptTemplate

from glow.constants import LLM_TEMPLATE


def read_system_info() -> str:
    """
    read the system information
    if it is windows, mac or linux
    """
    system = subprocess.run(["uname", "-a"], capture_output=True)
    return system.stdout.decode("utf-8")


class CommandLineChain(LLMChain):
    @classmethod
    def from_llm(cls, llm, verbose: bool = True):
        prompt = PromptTemplate(
            template=LLM_TEMPLATE,
            input_variables=["question", "system"],
        )

        return cls(
            llm=llm,
            prompt=prompt,
            verbose=verbose,
        )
