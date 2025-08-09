## OpenRouter/DeepSeek/Hugging Face Chat from Local Prompt Files

This module reads `system_prompt.txt` and `user_prompt.txt` from the current directory and sends them as chat prompts to a selected provider (Hugging Face by default).

### Prerequisites
- Python 3.9+
- An API key for your chosen provider

### Setup
1. Install dependencies:

```
pip install -r requirements.txt
```

2. Set your API key (PowerShell on Windows). For Hugging Face:
```
$env:HUGGINGFACE_API_KEY = "YOUR_HF_TOKEN"
```
Alternatively:
- OpenRouter: `$env:OPENROUTER_API_KEY = "YOUR_OPENROUTER_KEY"`
- DeepSeek: `$env:DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_KEY"`

Optional headers for OpenRouter (improves routing/analytics):
```
$env:OPENROUTER_SITE_URL = "https://your-site.example"
$env:OPENROUTER_APP_NAME = "Your App Name"
```

3. (Optional) Set up Telegram bot:
```
$env:TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
$env:TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
```

To get these:
- Create a bot with @BotFather on Telegram
- Get your chat ID by messaging @userinfobot

### Usage
1. Edit `system_prompt.txt` and `user_prompt.txt` with your instructions (user file optional).
2. Run the module (defaults to Hugging Face Zephyr 7B Beta):
```
python openrouter_chat.py --provider huggingface --model HuggingFaceH4/zephyr-7b-beta
```

Provider selection:
- Auto-detect (default): picks based on which API key is set (HF preferred)
- Force provider: `--provider huggingface|openrouter|deepseek`
- Free model features (`--list-free`, `--free-only`) apply only to OpenRouter

Arguments:
- `--model`: Provider-specific model ID (default HF: `HuggingFaceH4/zephyr-7b-beta`).
- `--dir`: Directory to read the prompt files from (default: current directory).
- `--system`: Override system prompt file name (default: `system_prompt.txt`).
- `--user`: Override user prompt file name (default: `user_prompt.txt`).
- `--list-free`: Lists currently free models and exits (OpenRouter only).
- `--free-only`: Automatically chooses a free model and uses it for the request (OpenRouter only).
- `--no-telegram`: Disable sending to Telegram bot.
- `--telegram-document`: Send to Telegram as document instead of message.
- `--provider`: Choose `huggingface`, `openrouter`, or `deepseek`.

### Notes
- If `user_prompt.txt` is missing, the system prompt is treated as the user message.
- The response is sent to Telegram first (if configured) and saved into `generated_texts/` with a timestamped filename.
- Errors/fallbacks are logged to `logs.txt`.

### Hugging Face specifics
- We convert chat messages to a single prompt string for the Inference API.
- Automatic retry with exponential backoff is enabled for HF transient errors (429/5xx/timeouts).
- Adjust the model to any available text generation model you have access to.