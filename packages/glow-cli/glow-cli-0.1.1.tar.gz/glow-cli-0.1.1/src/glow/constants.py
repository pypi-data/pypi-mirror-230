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
