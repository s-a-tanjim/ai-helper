import os
from pprint import pprint

import openai

API_KEY_FILE = os.path.expanduser("~/.openai_api_key")
CONFIG_FILE = os.path.expanduser("~/.openai_config")


class Config:
    model = "davinci"

    # to dict
    def __dict__(self):
        return {
            "model": self.model
        }

    # set from dict
    def __init__(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                c = eval(f.read())
                self.model = c["model"]

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


def get_models():
    return openai.Model.list()


def set_model(model_name):
    config.model = model_name
    config.save()


if __name__ == '__main__':
    pprint(get_models())


def complete(prompt):
    return openai.Completion.create(
        engine=config.model,
        prompt=prompt,
        max_tokens=100,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )


def cost(total_tokens):
    model_rate = {
        "ada": 0.0004,
        "babbage": 0.0005,
        "curie": 0.002,
        "davinci": 0.02,
        "gpt-3.5-turbo": 0.002,
        "gpt-3.5-turbo-16k": 0.004,
    }.get(config.model, 0)

    return model_rate * (total_tokens / 1000)
