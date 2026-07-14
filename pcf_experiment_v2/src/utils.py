"""Shared utilities: paths, IO, retry/backoff, LLM client wrappers, JSON validation."""

import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RAW_DIR = OUTPUTS_DIR / "raw_responses"
JUDGED_DIR = OUTPUTS_DIR / "judged_responses"
VERIFIED_DIR = OUTPUTS_DIR / "verified_responses"
HUMAN_DIR = OUTPUTS_DIR / "human_annotations"
SUMMARY_DIR = OUTPUTS_DIR / "summaries"
FIGURES_DIR = OUTPUTS_DIR / "figures"
LOG_DIR = OUTPUTS_DIR / "logs"


def ensure_dirs():
    for d in [RAW_DIR, JUDGED_DIR, VERIFIED_DIR, HUMAN_DIR, SUMMARY_DIR, FIGURES_DIR, LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def get_logger(name="pcf"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ensure_dirs()
        fh = logging.FileHandler(LOG_DIR / "experiment.log", encoding="utf-8")
        sh = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    # utf-8-sig tolerates a BOM (e.g. files edited via PowerShell)
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_llm_json(text):
    """Parse a JSON object from LLM output, tolerating markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in output: {text[:200]!r}")
    return json.loads(text[start:end + 1])


def call_with_retry(fn, max_attempts=3, base_delay=2.0, logger=None):
    """Call fn() with exponential backoff. Returns (result, retry_count)."""
    last_err = None
    for attempt in range(max_attempts):
        try:
            return fn(), attempt
        except Exception as e:  # noqa: BLE001 - API errors vary by provider
            last_err = e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            if logger:
                logger.warning("Attempt %d failed (%s); retrying in %.1fs", attempt + 1, e, delay)
            time.sleep(delay)
    raise RuntimeError(f"All {max_attempts} attempts failed: {last_err}") from last_err


# ---------------------------------------------------------------------------
# LLM client wrappers. DRY_RUN=1 (env var) returns canned outputs so the whole
# pipeline can be exercised without API keys.
# ---------------------------------------------------------------------------

DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"

_openai_client = None
_anthropic_client = None


def _get_openai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI()
    return _openai_client


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def chat_completion(model_cfg, messages, dry_run_text="[DRY RUN] In-character placeholder response."):
    """Provider-agnostic chat call.

    messages: list of {"role": ..., "content": ...}; a leading "system" message is allowed.
    Returns dict: {text, latency_seconds, usage, retry_count}.
    """
    if DRY_RUN:
        return {"text": dry_run_text, "latency_seconds": 0.0, "usage": {}, "retry_count": 0}

    provider = model_cfg["provider"]
    t0 = time.time()

    if provider == "openai":
        def do_call():
            kwargs = dict(
                model=model_cfg["model"],
                messages=messages,
                temperature=model_cfg.get("temperature", 0.7),
                top_p=model_cfg.get("top_p", 1.0),
                max_tokens=model_cfg.get("max_tokens", 500),
                frequency_penalty=model_cfg.get("frequency_penalty", 0.0),
                presence_penalty=model_cfg.get("presence_penalty", 0.0),
            )
            if model_cfg.get("seed") is not None:
                kwargs["seed"] = model_cfg["seed"]
            return _get_openai().chat.completions.create(**kwargs)

        resp, retries = call_with_retry(do_call, logger=get_logger())
        usage = resp.usage.model_dump() if resp.usage else {}
        text = resp.choices[0].message.content

    elif provider == "anthropic":
        system = ""
        chat = []
        for m in messages:
            if m["role"] == "system":
                system += m["content"] + "\n"
            else:
                chat.append(m)

        def do_call():
            kwargs = dict(
                model=model_cfg["model"],
                messages=chat,
                temperature=model_cfg.get("temperature", 0.0),
                max_tokens=model_cfg.get("max_tokens", 1024),
            )
            if system.strip():
                kwargs["system"] = system.strip()
            return _get_anthropic().messages.create(**kwargs)

        resp, retries = call_with_retry(do_call, logger=get_logger())
        usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
        text = "".join(b.text for b in resp.content if b.type == "text")
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return {
        "text": text,
        "latency_seconds": round(time.time() - t0, 3),
        "usage": usage,
        "retry_count": retries,
    }
