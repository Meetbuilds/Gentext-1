import argparse
import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
from openrouter_chat import chat_from_local_prompts
import httpx
from dotenv import load_dotenv


API_URL = "https://openrouter.ai/api/v1/chat/completions"


def read_text_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_headers(api_key: Optional[str]) -> dict:
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    site_url = os.getenv("OPENROUTER_SITE_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name
    return headers


def create_client(timeout_seconds: int = 120) -> httpx.Client:
    return httpx.Client(timeout=httpx.Timeout(timeout_seconds))


def send_chat_request(
    model: str,
    system_text: str,
    user_text: str,
    api_key: str,
    temperature: Optional[float] = None,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ],
    }
    if temperature is not None:
        payload["temperature"] = temperature

    headers = build_headers(api_key)

    with create_client() as client:
        response = client.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Unexpected API response format: {data}")


def parse_price(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value.strip())
    except Exception:
        return None
    return None


def is_free_model(model_obj: Dict[str, Any]) -> bool:
    pricing = model_obj.get("pricing") or {}
    p_prompt = parse_price(pricing.get("prompt"))
    p_completion = parse_price(pricing.get("completion"))
    if p_prompt is None or p_completion is None:
        return False
    return p_prompt == 0.0 and p_completion == 0.0


def fetch_free_models(api_key: Optional[str]) -> List[Dict[str, Any]]:
    url = "https://openrouter.ai/api/v1/models"
    headers = build_headers(api_key)
    with create_client() as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        payload = resp.json()
    models = payload.get("data") or payload.get("models") or []
    free = [m for m in models if is_free_model(m)]
    # Heuristic: filter out disabled/deprecated if flags exist
    result: List[Dict[str, Any]] = []
    for m in free:
        if m.get("archived") or m.get("disabled"):
            continue
        result.append(m)
    return result


def choose_best_free_model(models: List[Dict[str, Any]]) -> Optional[str]:
    if not models:
        return None
    def sort_key(m: Dict[str, Any]):
        ctx = m.get("context_length") or 0
        quality = m.get("quality") or 0
        mid = m.get("id") or ""
        return (-int(ctx or 0), -int(quality or 0), mid)
    best = sorted(models, key=sort_key)[0]
    return best.get("id")


def save_text_with_timestamp(text: str, out_dir: str = "generated_texts") -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{ts}.txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def log_message(message: str, log_file: str = "logs.txt"):
    os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")


def chat_from_local_prompts(
    model: str = "openrouter/auto",
    directory: str = ".",
    system_filename: str = "system_prompt.txt",
    user_filename: str = "user_prompt.txt",
    temperature: Optional[float] = None,
    free_only: bool = False,
) -> str:
    """Load system/user prompts from files and send a chat completion to OpenRouter.

    Raises:
        FileNotFoundError: If either prompt file is missing
        RuntimeError: If env var OPENROUTER_API_KEY is missing or API response is invalid
        httpx.HTTPError: For network/HTTP errors
    """
    load_dotenv()

    system_path = os.path.join(directory, system_filename)
    user_path = os.path.join(directory, user_filename)

    system_text = read_text_file(system_path)
    user_text = read_text_file(user_path)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment")

    selected_model = model
    if free_only:
        free_models = fetch_free_models(api_key)
        chosen = choose_best_free_model(free_models)
        if not chosen:
            raise RuntimeError("No free models available to select")
        selected_model = chosen

    try:
        reply = send_chat_request(
            model=selected_model,
            system_text=system_text,
            user_text=user_text,
            api_key=api_key,
            temperature=temperature,
        )
        save_text_with_timestamp(reply)
        return reply
    except httpx.HTTPStatusError as http_err:
        if http_err.response is not None and http_err.response.status_code == 402 and not free_only:
            # Attempt automatic fallback to a free model
            log_message(f"402 error with model {selected_model}, attempting free model fallback")
            free_models = fetch_free_models(api_key)
            chosen = choose_best_free_model(free_models)
            if not chosen or chosen == selected_model:
                log_message(f"Free model fallback failed: no suitable model found")
                raise
            log_message(f"Retrying with free model: {chosen}")
            reply = send_chat_request(
                model=chosen,
                system_text=system_text,
                user_text=user_text,
                api_key=api_key,
                temperature=temperature,
            )
            save_text_with_timestamp(reply)
            return reply
        else:
            log_message(f"HTTP error: {http_err}")
        raise


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send system/user prompts from files to OpenRouter Chat API",
    )
    parser.add_argument(
        "--model",
        default="openrouter/auto",
        help="Model ID to use (default: openrouter/auto)",
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Directory to read prompt files from (default: current directory)",
    )
    parser.add_argument(
        "--system",
        default="system_prompt.txt",
        help="System prompt file name (default: system_prompt.txt)",
    )
    parser.add_argument(
        "--user",
        default="user_prompt.txt",
        help="User prompt file name (default: user_prompt.txt)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature (optional)",
    )
    parser.add_argument(
        "--list-free",
        action="store_true",
        help="List free models available via OpenRouter and exit",
    )
    parser.add_argument(
        "--free-only",
        action="store_true",
        help="Automatically choose a free model and use it for this request",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    load_dotenv()

    args = parse_args(argv)

    if args.list_free:
        try:
            free_models = fetch_free_models(os.getenv("OPENROUTER_API_KEY"))
        except httpx.HTTPError as http_err:
            print(f"Could not fetch models: {http_err}", file=sys.stderr)
            return 2
        if not free_models:
            print("No free models found at this time. Try again later or fund your account.", file=sys.stderr)
            return 0
        print("Free models available:")
        for m in free_models:
            mid = m.get("id") or m.get("name") or "<unknown>"
            ctx = m.get("context_length") or m.get("context")
            if ctx:
                print(f"- {mid} (ctx: {ctx})")
            else:
                print(f"- {mid}")
        print("\nUse one with: python openrouter_chat.py --model <model-id>")
        return 0
    system_path = os.path.join(args.dir, args.system)
    user_path = os.path.join(args.dir, args.user)

    try:
        system_text = read_text_file(system_path)
        user_text = read_text_file(user_path)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set. Please set it in your environment.", file=sys.stderr)
        return 1

    # Determine model selection strategy
    selected_model = args.model
    if args.free_only:
        try:
            free_models = fetch_free_models(api_key)
            chosen = choose_best_free_model(free_models)
            if not chosen:
                print("No free models available to select.", file=sys.stderr)
                return 1
            selected_model = chosen
        except httpx.HTTPError as http_err:
            print(f"Could not fetch free models: {http_err}", file=sys.stderr)
            return 2

    try:
        reply = chat_from_local_prompts(
            model=selected_model,
            directory=args.dir,
            system_filename=args.system,
            user_filename=args.user,
            temperature=args.temperature,
            free_only=False,
        )
    except httpx.HTTPStatusError as http_err:
        if http_err.response is not None and http_err.response.status_code == 402:
            print("Payment required (402).", file=sys.stderr)
            if not args.free_only:
                # Attempt automatic fallback to a free model
                try:
                    free_models = fetch_free_models(api_key)
                    chosen = choose_best_free_model(free_models)
                    if chosen and chosen != selected_model:
                        print(f"Retrying with free model: {chosen}", file=sys.stderr)
                        reply = chat_from_local_prompts(
                            model=chosen,
                            directory=args.dir,
                            system_filename=args.system,
                            user_filename=args.user,
                            temperature=args.temperature,
                            free_only=True,
                        )
                        print(reply)
                        return 0
                except Exception as err:
                    print(f"Auto-free fallback failed: {err}", file=sys.stderr)
            print("Add funds or run with --free-only to auto-pick a free model.", file=sys.stderr)
        else:
            print(f"HTTP error: {http_err}", file=sys.stderr)
        return 2
    except httpx.HTTPError as http_err:
        print(f"HTTP error: {http_err}", file=sys.stderr)
        return 2
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        return 3

    print(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

