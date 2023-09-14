from typing import Any, Dict, Optional

from glow.colors import cprint
from glow.constants import GLOW_LLM_CONFIG, LLM_DEFAULT_CONFIG
from glow.utils.yaml import open_yaml_conf


def load_glow_llm_config() -> Dict[str, Any]:
    """
    Load the configuration for LLM

    If not found, create a default one
    """
    if GLOW_LLM_CONFIG.exists() is False:
        cprint("Configuration file for LLM not found, create default for you", "yellow")
        GLOW_LLM_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(GLOW_LLM_CONFIG, "w") as f:
            f.write(LLM_DEFAULT_CONFIG)
    return open_yaml_conf(GLOW_LLM_CONFIG)


def run_code(question: str) -> None:
    config = load_glow_llm_config()
    if "sdk" not in config:
        cprint(f"Please specify the sdk to use in {GLOW_LLM_CONFIG}, like `openai`", "red")
        return
    # make sure what sdk are we using
    if config["sdk"] == "openai":
        from glow.llm.openai import build_command_suggest

        command_suggest = build_command_suggest()
    else:
        cprint(f"sdk {config['sdk']} not supported for now", "yellow")
        return

    if command_suggest is None:
        # in case the loading llm failed
        return

    result = command_suggest(question)
    cprint(result, "header")


def run_llm(question: str, system_content: Optional[str] = None) -> None:
    config = load_glow_llm_config()
    if "sdk" not in config:
        cprint(f"Please specify the sdk to use in {GLOW_LLM_CONFIG}, like `openai`", "red")
        return
    # make sure what sdk are we using
    if config["sdk"] == "openai":
        from glow.llm.openai import build_llm_ask

        ask = build_llm_ask()

    else:
        cprint(f"sdk {config['sdk']} not supported for now", "yellow")
        return
    if ask is None:
        # in case the loading llm failed
        return
    result = ask(question, system_content)
    if result is not None:
        cprint(result, "header")
