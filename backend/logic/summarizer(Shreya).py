"""
summarizer.py — Ollama LLM Summarizer Module (Person 3: Shreya)

Sends meeting transcript snippets to a local Ollama instance and
returns a cleanly parsed JSON array of action items.
"""

import json
import re
from typing import Any, Dict, List, Optional

import httpx


# ------------------------------------------------------------------ #
#  Configuration
# ------------------------------------------------------------------ #

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
DEFAULT_MODEL = "phi3"          # fallback; llama3 also supported
REQUEST_TIMEOUT = 60.0          # seconds – local LLMs can be slow


# ------------------------------------------------------------------ #
#  Prompt template
# ------------------------------------------------------------------ #

SYSTEM_PROMPT = (
    "You are a concise meeting-assistant AI. "
    "You will receive a snippet from a live meeting transcript. "
    "Your ONLY job is to extract action items from the text.\n\n"
    "RULES:\n"
    "1. Output STRICTLY a JSON array of action-item strings.\n"
    "2. Include at most 3 action items.\n"
    "3. Each item must be a single short sentence.\n"
    "4. Do NOT include any introductory text, explanation, or markdown.\n"
    "5. If there are no clear action items, return an empty array: []\n\n"
    "Example output:\n"
    '[\"Submit the budget report by Friday\", '
    '\"Schedule a follow-up call with the client\", '
    '\"Share the updated design mockups with the team\"]'
)


def _build_prompt(snippet: str) -> str:
    """Combine the system prompt with the user-supplied snippet."""
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- MEETING SNIPPET START ---\n"
        f"{snippet}\n"
        f"--- MEETING SNIPPET END ---\n\n"
        f"Output the JSON array now:"
    )


# ------------------------------------------------------------------ #
#  Response parser
# ------------------------------------------------------------------ #

def _parse_action_items(raw_text: str) -> List[str]:
    """
    Attempt to extract a JSON array from the LLM's raw response.

    The model *should* return a bare JSON array, but sometimes it wraps
    it in markdown code fences or adds preamble text.  This function
    handles those common edge cases gracefully.
    """
    text = raw_text.strip()

    # Strip markdown code fences if present (```json ... ```)
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Try to locate the first JSON array in the response
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                # Ensure every element is a string and cap at 3
                return [str(item) for item in parsed[:3]]
        except json.JSONDecodeError:
            pass

    # Last resort: if the model returned plain numbered lines, parse them
    lines = [
        re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith(("{", "[", "]", "}"))
    ]
    return lines[:3] if lines else []


# ------------------------------------------------------------------ #
#  Public async API
# ------------------------------------------------------------------ #

async def summarize_snippet(
    snippet: str,
    model: str = DEFAULT_MODEL,
    ollama_url: str = OLLAMA_GENERATE_ENDPOINT,
    timeout: float = REQUEST_TIMEOUT,
) -> Dict[str, Any]:
    """
    Send a meeting snippet to the local Ollama instance and return
    a clean JSON object with the extracted action items.

    Args:
        snippet:    The context text extracted by the KeywordScanner.
        model:      Ollama model name (e.g. "phi3", "llama3").
        ollama_url: Full URL to the Ollama generate endpoint.
        timeout:    HTTP request timeout in seconds.

    Returns:
        {
          "success": bool,
          "action_items": ["...", "...", "..."],
          "raw_response": str,      # raw LLM output for debugging
          "error": str | None
        }
    """
    prompt = _build_prompt(snippet)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,           # get the full response in one shot
        "options": {
            "temperature": 0.3,    # low temp → deterministic output
            "num_predict": 256,    # cap token count for speed
        },
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(ollama_url, json=payload)
            response.raise_for_status()

        body = response.json()
        raw_response = body.get("response", "")

        action_items = _parse_action_items(raw_response)

        return {
            "success": True,
            "action_items": action_items,
            "raw_response": raw_response,
            "error": None,
        }

    except httpx.ConnectError:
        return {
            "success": False,
            "action_items": [],
            "raw_response": "",
            "error": (
                "Could not connect to Ollama. "
                "Make sure it is running on "
                f"{OLLAMA_BASE_URL}"
            ),
        }
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "action_items": [],
            "raw_response": "",
            "error": f"Ollama returned HTTP {exc.response.status_code}: {exc.response.text}",
        }
    except Exception as exc:
        return {
            "success": False,
            "action_items": [],
            "raw_response": "",
            "error": f"Unexpected error: {exc}",
        }


async def summarize_meeting(
    snippets: List[str],
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Convenience wrapper: summarize an entire meeting by concatenating
    all important snippets into one block before querying the LLM.

    Returns the same dict shape as `summarize_snippet`.
    """
    if not snippets:
        return {
            "success": True,
            "action_items": [],
            "raw_response": "",
            "error": None,
        }

    combined = "\n\n".join(snippets)
    return await summarize_snippet(combined, model=model)
