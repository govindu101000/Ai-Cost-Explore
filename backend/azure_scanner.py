import json
import shutil
import subprocess
from typing import Dict, List


class AzureCLIError(Exception):
    pass


class AzNotInstalled(AzureCLIError):
    pass


class AzNotLoggedIn(AzureCLIError):
    pass


class ResourceGroupNotFound(AzureCLIError):
    pass


def _get_az_path() -> str:
    """Get the full path to the az CLI executable."""
    # Try common locations
    paths = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
    ]
    for path in paths:
        try:
            subprocess.run([path, "--version"], capture_output=True, check=True)
            return path
        except:
            pass
    
    # Fall back to PATH lookup
    az_path = shutil.which("az")
    if az_path:
        return az_path
    raise AzNotInstalled("Azure CLI ('az') not found")


AZ_PATH = None

def _check_az_installed() -> None:
    global AZ_PATH
    if AZ_PATH is None:
        AZ_PATH = _get_az_path()


def list_resource_groups() -> List[Dict]:
    """Return a list of resource groups (name, location, id, tags).

    Raises AzNotInstalled or AzNotLoggedIn on failure.
    """
    _check_az_installed()
    try:
        res = subprocess.run([AZ_PATH, "group", "list", "-o", "json"], capture_output=True, text=True, check=True)
        groups = json.loads(res.stdout)
        return [
            {"name": g.get("name"), "location": g.get("location"), "id": g.get("id"), "tags": g.get("tags") or {}}
            for g in groups
        ]
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").lower()
        if "please run 'az login'" in stderr or "az login" in stderr or "not logged in" in stderr:
            raise AzNotLoggedIn(stderr)
        raise AzureCLIError(e.stderr or e.stdout or str(e))


def scan_resource_group(resource_group: str) -> List[Dict]:
    """Scan resources in a resource group and return structured info.

    Each resource dict contains: type, name, location, sku, tags
    """
    _check_az_installed()
    try:
        res = subprocess.run([AZ_PATH, "resource", "list", "--resource-group", resource_group, "-o", "json"], capture_output=True, text=True, check=True)
        items = json.loads(res.stdout)
        parsed = []
        for it in items:
            sku = None
            sku_field = it.get("sku")
            if isinstance(sku_field, dict):
                sku = sku_field.get("name")

            # sometimes SKU is nested under properties.sku
            props = it.get("properties") or {}
            if not sku and isinstance(props.get("sku"), dict):
                sku = props.get("sku").get("name")

            parsed.append({
                "type": it.get("type"),
                "name": it.get("name"),
                "location": it.get("location"),
                "sku": sku,
                "tags": it.get("tags") or {},
            })
        return parsed
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").lower()
        if "resource group" in stderr and "could not be found" in stderr:
            raise ResourceGroupNotFound(stderr)
        if "please run 'az login'" in stderr or "az login" in stderr or "not logged in" in stderr:
            raise AzNotLoggedIn(stderr)
        raise AzureCLIError(e.stderr or e.stdout or str(e))
