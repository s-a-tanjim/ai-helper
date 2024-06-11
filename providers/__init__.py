from providers.base import ChatProvider
from providers.OpenAI import OpenAIChatProvider
from providers.Google import GoogleChatProvider
from providers.Ollama import OllamaChatProvider
from providers.Groq import GroqChatProvider
from providers.Cohere import CohereChatProvider
from providers.Ai21 import Ai21ChatProvider
from providers.NLPCloud import NLPCloudChatProvider


def get_chat_provider(provider):
    return {
        "ollama": OllamaChatProvider,
        "openai": OpenAIChatProvider,
        "google": GoogleChatProvider,
        "groq": GroqChatProvider,
        'cohere': CohereChatProvider,
        'ai21': Ai21ChatProvider,
        'nlpcloud': NLPCloudChatProvider,
    }[provider]()
