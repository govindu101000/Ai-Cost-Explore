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
    

def analyze_resources(resources: list):
    """
    Converts Azure resources into:
    - issues
    - suggestions
    - summary
    """

    issues = []
    suggestions = []

    for r in resources:

        r_type = (r.get("type") or "").lower()

        # -------------------------
        # Example RULES (extend later with LLM)
        # -------------------------

        if "vm" in r_type:
            issues.append({
                "resource_name": r.get("name"),
                "resource_type": r_type,
                "issue_type": "Potential idle VM",
                "severity": "medium",
                "description": "VM may be underutilized.",
                "business_impact": "Unnecessary compute cost",
                "recommendation": "Enable auto-shutdown or resize",
                "estimated_savings": "$20-80/month",
                "best_practice": "Use auto-shutdown schedules",
                "fix_command": "az vm deallocate --name <vm-name>"
            })

            suggestions.append({
                "title": f"Optimize VM: {r.get('name')}",
                "description": "Enable auto-shutdown or scaling policies",
                "estimated_savings": "$20-80/month"
            })

        elif "disk" in r_type:
            suggestions.append({
                "title": f"Check disk usage: {r.get('name')}",
                "description": "Consider moving to lower tier storage",
                "estimated_savings": "$5-20/month"
            })

    return {
        "summary": (
            f"Scanned {len(resources)} resources. "
            f"Found {len(issues)} optimization opportunities."
        ),
        "issues": issues,
        "suggestions": suggestions
    }