<img src="https://github.com/s-a-tanjim/ai-helper/blob/master/images/demo.gif" width="100%"/>

# AI CLI

Provides a cli interface to interact with any AI providers.

## Getting Started

### Providers

| Provider  | Status | Get an API key                                             |
|-----------|--------|------------------------------------------------------------|
| Google    | ✅      | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| OpenAI    | ✅      | [OpenAI](https://platform.openai.com/api-keys)             |
| Groq      | ✅      | [Groq](https://console.groq.com/keys)                      |
| Cohere    | ✅      | [Cohere](https://dashboard.cohere.com/api-keys)            |
| Ai21      | ✅      | [Ai21](https://studio.ai21.com/account/api-key)            |
| NLP Cloud | ✅      | [NLP Cloud](https://nlpcloud.com/home/token)               |
| Ollama    | ✅      | [Not Required, Just Install](https://ollama.com/download)  |
| Claude    | ❌      |                                                            |

### Commands

| Command         | Description                                    |
|-----------------|------------------------------------------------|
| `provider`      | Select a provider                              |
| `model`         | Select a model                                 |
| `cli`           | Always gives bash/powershell commands          |
| `gr`            | Checks for grammar mistakes, provides variants |
| `chat`          | Chat with AI                                   |
| `summary`       | Summarize text                                 |
| `commit`        | Auto generate commit message & does the commit |
| `custom create` | Create a custom prompt with your own prompt    |
| `custom list`   | List custom prompts                            |
| `<any>`         | Use previously created custom prompt           |

## Usage

```bash
ai chat 'What is the capital of France?'
ai chat How is the weather today? # No quotes needed
ai chat # Will ask for input

ai cli 'How to install python?'
ai cli --provider google # Ignores the default provider, and uses google
# Press double enter to exit and get the command to clipboard

ai custom create puppy 'You are a puppy, Only respond with barks'
ai puppy 'What is the capital of France?'
ai puppy -p google -m gemini-1.5-pro 
```

## Installation

```bash
git clone https://github.com/anwar3606/ai-helper
cd ai-helper
pip install .
```

# Make it available in bin
```bash
sudo ln -s <path-of-project>/venv/bin/ai /usr/bin/ai
```