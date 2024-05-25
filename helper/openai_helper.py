import os
from pprint import pprint

import ollama
import openai

from helper.console_helper import console

API_KEY_FILE = os.path.expanduser("~/.openai_api_key")
CONFIG_FILE = os.path.expanduser("~/.openai_config")


class Config:
    model = "davinci"
    provider = "openai"

    # to dict
    def __dict__(self):
        return {
            "model": self.model,
            'provider': self.provider
        }

    # set from dict
    def __init__(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                c = eval(f.read())
                self.model = c["model"]
                self.provider = c.get("provider", "openai")

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            f.write(str(self.__dict__()))


config = Config()


def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE) as f:
            return f.read().strip()


try:
    openai.api_key = get_api_key()
    if not openai.api_key:
        raise TypeError
except (FileNotFoundError, TypeError):
    save_api_key = input("Enter your OpenAI API key: ")
    with open(API_KEY_FILE, "w") as f:
        f.write(save_api_key)
    openai.api_key = save_api_key


def set_provider(provider, save=True):
    config.provider = provider

    if save:
        console.log(f"Saving provider: {provider}")
        config.save()


def get_models():
    if config.provider == "ollama":
        models = ollama.list()['models']
        # convert each dict to object to a vritual class
        for i in range(len(models)):
            models[i] = type('obj', (object,), models[i])
            models[i].id = models[i].name
        return models
    elif config.provider == "openai":
        return openai.models.list()


def set_model(model_name, save=True):
    config.model = model_name
    if save:
        console.log(f"Saving model: {model_name}")
        config.save()


if __name__ == '__main__':
    pprint(get_models())


def cost(total_input_tokens: int, total_output_tokens: int) -> float:
    million = 1_000_000

    if config.provider == "ollama":
        return 0

    model_rate = {
        "gpt-3.5-turbo": {'input': 0.50 / million, 'output': 1.50 / million},
        "gpt-4": {'input': 10.00 / million, 'output': 30.00 / million},
        'gpt-4o': {'input': 5.00 / million, 'output': 15.00 / million},
    }.get(config.model, {'input': 0.0, 'output': 0.0})

    return round(total_input_tokens * model_rate['input'] + total_output_tokens * model_rate['output'], 4)


def chat_completion(messages: list, **kwargs):
    if config.provider == "ollama":
        return ollama.chat(
            model=config.model,
            messages=messages)
    elif config.provider == "openai":
        return openai.chat.completions.create(
            model=config.model,
            messages=messages,
            **kwargs
        )


def get_model_details():
    if config.provider == "ollama":
        return ollama.show(config.model)
    elif config.provider == "openai":
        return openai.models.retrieve(config.model)
