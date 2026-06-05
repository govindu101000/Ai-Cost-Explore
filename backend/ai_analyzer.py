import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.1:latest"
)


def build_prompt(resources):

    return f"""
You are an expert Azure Cloud Cost Optimization Architect.

Analyze the provided Azure resources.

Identify:

1. Over-provisioned resources
2. Unused resources
3. Idle resources
4. Incorrect SKUs
5. Cost optimization opportunities
6. Security-related cost waste
7. Storage optimization opportunities

Return ONLY VALID JSON.

Required format:

{{
  "summary": "...",
  "estimated_total_monthly_savings": "$XXX",

  "issues": [
    {{
      "resource_name": "...",
      "resource_type": "...",

      "issue_type":
      "Over-Provisioned | Unused | Idle | Misconfigured | Cost Optimization",

      "severity":
      "high | medium | low",

      "description":
      "...",

      "business_impact":
      "...",

      "recommendation":
      "...",

      "estimated_savings":
      "$XX/month",

      "fix_command":
      "az ...",

      "best_practice":
      "..."
    }}
  ]
}}

Resources:

{json.dumps(resources, indent=2)}
"""
    

def analyze_resources(resources):

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": build_prompt(resources),
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    data = response.json()

    try:

        return json.loads(
            data["response"]
        )

    except Exception:

        return {
            "summary":
            "Unable to parse model response.",

            "estimated_total_monthly_savings":
            "Unknown",

            "issues": []
        }