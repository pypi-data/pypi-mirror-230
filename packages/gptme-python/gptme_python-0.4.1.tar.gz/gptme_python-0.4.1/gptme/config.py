import os
from typing import TypedDict

import toml


class Config(TypedDict):
    prompt: dict
    env: dict


ABOUT_ACTIVITYWATCH = """ActivityWatch is a free and open-source automated time-tracker that helps you track how you spend your time on your devices."""
ABOUT_GPTME = "gptme is a CLI to interact with large language models in a Chat-style interface, enabling the assistant to execute commands and code on the local machine, letting them assist in all kinds of development and terminal-based work."


default_config: Config = {
    "prompt": {
        "about_user": "I am a curious human programmer.",
        "response_preference": "Basic concepts don't need to be explained.",
        "project": {
            "activitywatch": ABOUT_ACTIVITYWATCH,
            "gptme": ABOUT_GPTME,
        },
    },
    "env": {"OPENAI_API_KEY": None},
}

_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = _load_config()
    return _config


def _load_config() -> Config:
    # Define the path to the config file
    config_path = os.path.expanduser("~/.config/gptme/config.toml")

    # Check if the config file exists
    if not os.path.exists(config_path):
        # If not, create it and write some default settings
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as config_file:
            toml.dump(default_config, config_file)
        print(f"Created config file at {config_path}")

    # Now you can read the settings from the config file like this:
    with open(config_path, "r") as config_file:
        config: dict = toml.load(config_file)

        # TODO: validate
        config = Config(**config)  # type: ignore

    return config  # type: ignore


if __name__ == "__main__":
    config = get_config()
    print(config)
