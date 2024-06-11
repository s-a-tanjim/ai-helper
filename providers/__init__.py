from providers.Google import GoogleChatProvider
from providers.Groq import GroqChatProvider
from providers.Ollama import OllamaChatProvider
from providers.OpenAI import OpenAIChatProvider
from providers.base import ChatProvider


def get_chat_provider(provider):
    return {
        "ollama": OllamaChatProvider,
        "openai": OpenAIChatProvider,
        "google": GoogleChatProvider,
        "groq": GroqChatProvider
    }[provider]()
