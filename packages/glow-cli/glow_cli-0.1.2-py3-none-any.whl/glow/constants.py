import os
from pathlib import Path

# the ASCII art for the logo
ASCII_ART = """
   ________    ____ _       __
  / ____/ /   / __ \ |     / /
 / / __/ /   / / / / | /| / /
/ /_/ / /___/ /_/ /| |/ |/ /
\____/_____/\____/ |__/|__/
"""
GLOW_CONF: Path = Path.home() / ".glow"
GLOW_CONF.mkdir(exist_ok=True, parents=True)
GLOW_COMMANDS = GLOW_CONF / "commands"
GLOW_COMMANDS.mkdir(exist_ok=True, parents=True)
GLOW_ENV_FILE = Path(os.environ.get("GLOW_ENV_FILE", GLOW_CONF / ".env"))
GLOW_LLM_CONFIG = GLOW_CONF / "llm" / "config.yml"

LLM_TEMPLATE = """
   based on {question}, generate bash script that we can run in {system}.
   Please answer with the script only.
   start the script with: 🍔🍔🍔
   end the script with: 🍟🍟🍟
   """

LLM_DEFAULT_CONFIG = """
sdk: openai
kwargs:
  model: gpt-3.5-turbo-16k
"""
