import os


class Config:

    def __init__(self, config_file_path, default: dict = None):
        self._data = {}
        self._config_file_path = config_file_path
        self.read()

        if not self._data:
            self._data = default or {}
            self.save()

    def __getattribute__(self, name):
        if name.startswith("_") or name not in self._data:
            return super().__getattribute__(name)
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def save(self):
        with open(self._config_file_path, "w") as f:
            f.write(str(self._data))

    def read(self):
        if os.path.exists(self._config_file_path):
            with open(self._config_file_path) as config_file:
                try:
                    content = eval(config_file.read())
                except SyntaxError:
                    content = {}
                self._data = content


global_config = Config(
    os.path.expanduser("~/.ai_config"),
    {
        "provider": "openai",
        "providers": ["openai", "ollama", "google"],
        "prompts": {}
    }
)
