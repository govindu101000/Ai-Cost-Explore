import os
import json
from typing import List, Dict, Any

import openai
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


class OpenAIError(Exception):
    pass


def _build_prompt(resources: List[Dict[str, Any]]) -> str:
    prompt = (
        "You are a cloud cost optimization assistant. "
        "Analyze the following Azure resources for over-provisioning, unused/idle resources, "
        "misconfigurations, wrong pricing tiers, and cost optimization opportunities.\n\n"
    )
    prompt += "Respond with a single JSON object with keys: summary, issues (array), estimated_savings, actionable_commands.\n"
    prompt += (
        "Each issue should include: resource (name), resource_type, description, severity (high|medium|low), "
        "estimated_savings (number, USD), and fix_commands (array of Azure CLI commands).\n\n"
    )
    prompt += "Resources (JSON array):\n"
    prompt += json.dumps(resources, indent=2)
    prompt += "\n\nReturn only JSON (no extra commentary)."
    return prompt


def analyze_with_ai(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        raise OpenAIError("OPENAI_API_KEY not set in environment")

    prompt = _build_prompt(resources)

    try:
        resp = openai.responses.create(
            model="gpt-4o",
            input=prompt,
            temperature=0.2,
            max_output_tokens=1000,
        )
        content = getattr(resp, "output_text", None)
        if content is None:
            # fallback to raw response extraction
            if hasattr(resp, "output") and resp.output:
                fragments = []
                for item in resp.output:
                    content_items = getattr(item, "content", []) if hasattr(item, "content") else item.get("content", [])
                    for content_item in content_items:
                        if getattr(content_item, "type", None) == "output_text":
                            fragments.append(getattr(content_item, "text", ""))
                content = "\n".join(fragments)
            else:
                content = str(resp)

        # Try to extract JSON payload from response
        text = content.strip()
        # If code fence present, extract inner content
        if text.startswith("```") and text.endswith("```"):
            # remove backticks and optional json marker
            inner = "\n".join(text.splitlines()[1:-1]).strip()
            text = inner

        try:
            parsed = json.loads(text)
            return parsed
        except Exception:
            # fallback: try to find first JSON object in text
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except Exception:
                    pass
            return {"text": content}

    except Exception as e:
        raise OpenAIError(str(e))
