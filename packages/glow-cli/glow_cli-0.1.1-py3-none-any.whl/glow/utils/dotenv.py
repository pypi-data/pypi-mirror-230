from pathlib import Path
from dotenv import load_dotenv
from glow.utils.colors import bcolors


def load_dot_env_file(file: Path) -> None:
    """
    Load env file given path, print error while not found
    """
    if Path(file).exists():
        load_dotenv(file)
    else:
        print(bcolors(f"{file} not found for env file", "red"))
