## OpenRouter Chat from Local Prompt Files

This module reads `system_prompt.txt` and `user_prompt.txt` from the current directory and sends them as system and user messages to the OpenRouter Chat Completions API.

### Prerequisites
- Python 3.9+
- An OpenRouter API key

### Setup
1. Install dependencies:

```
pip install -r requirements.txt
```

2. Set your API key (PowerShell on Windows):

```
$env:OPENROUTER_API_KEY = "YOUR_API_KEY_HERE"
```

Optional headers (improves routing/analytics):

```
$env:OPENROUTER_SITE_URL = "https://your-site.example"
$env:OPENROUTER_APP_NAME = "Your App Name"
```

### Usage
1. Edit `system_prompt.txt` and `user_prompt.txt` with your instructions.
2. Run the module:

```
python openrouter_chat.py --model openrouter/auto
```

Arguments:
- `--model`: Model ID to use (default: `openrouter/auto`). Any valid OpenRouter model ID works.
- `--dir`: Directory to read the prompt files from (default: current directory).
- `--system`: Override system prompt file name (default: `system_prompt.txt`).
- `--user`: Override user prompt file name (default: `user_prompt.txt`).
- `--list-free`: Lists currently free models and exits.
- `--free-only`: Automatically chooses a free model and uses it for the request. If none are available, exits.

### Notes
- The script reads the entire contents of both files and sends them as messages:
  - System message: contents of `system_prompt.txt`
  - User message: contents of `user_prompt.txt`
- The response assistant message is printed to stdout.
- Every successful response is also saved into `generated_texts/` with a timestamped filename like `YYYY-MM-DD_HH-MM-SS.txt`.
- Fallback attempts and errors are logged to `logs.txt` for debugging.

### Find and use a free model
1. List free models:
```
python openrouter_chat.py --list-free
```
2. Pick an ID from the list (e.g., `some/free-model-id`).
3. Run with that model:
```
python openrouter_chat.py --model some/free-model-id
```

Or skip manual selection and let the script auto-pick a free model:
```
python openrouter_chat.py --free-only
```

All successful replies are saved to `generated_texts/` automatically. Fallback attempts and errors are logged to `logs.txt`.


