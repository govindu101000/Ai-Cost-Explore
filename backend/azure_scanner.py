import json
import subprocess
import shutil
import os


class AzureScannerError(Exception):
    pass


def _get_az_path():
    """
    Find Azure CLI executable in Windows even if PATH is broken.
    """

    # 1. normal PATH lookup
    az = shutil.which("az")
    if az:
        return az

    # 2. Windows default install locations
    possible_paths = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Azure\CLI\wbin\az.cmd",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def _run_az_command(command):
    az_path = _get_az_path()

    if not az_path:
        raise AzureScannerError(
            "Azure CLI not found. Install Azure CLI: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
        )

    try:
        result = subprocess.run(
            [az_path] + command[1:],  # replace "az" with full path
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout:
            return "[]"

        return result.stdout

    except FileNotFoundError:
        raise AzureScannerError(
            "Azure CLI executable not found or not accessible."
        )

    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").lower()

        if "az login" in stderr or "not logged in" in stderr:
            raise AzureScannerError(
                "Azure CLI not logged in. Run: az login"
            )

        raise AzureScannerError(
            e.stderr or "Azure CLI command failed"
        )


# -----------------------------
# Resource Groups
# -----------------------------
def get_resource_groups():
    output = _run_az_command([
        "az",
        "group",
        "list",
        "-o",
        "json"
    ])

    groups = json.loads(output)

    return [
        {
            "name": g.get("name"),
            "location": g.get("location")
        }
        for g in groups
    ]


# -----------------------------
# Resources in RG
# -----------------------------
def get_resources(resource_group):
    output = _run_az_command([
        "az",
        "resource",
        "list",
        "--resource-group",
        resource_group,
        "-o",
        "json"
    ])

    resources = json.loads(output)

    parsed = []

    for r in resources:
        parsed.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "type": r.get("type"),
            "location": r.get("location"),
            "kind": r.get("kind"),
            "sku": r.get("sku"),
            "tags": r.get("tags", {})
        })

    return parsed