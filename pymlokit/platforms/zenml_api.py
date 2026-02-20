from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from pymlokit.utils.http import get_json, post_json


def _get_token(credential: str, api_url: str) -> str:
    # Credential format: username:password or token
    # If it looks like a token (no colon, long string), use it directly
    if ":" not in credential and len(credential) > 50:
        return credential
    
    # Otherwise assume username:password and try to login
    if ":" in credential:
        username, password = credential.split(":", 1)
        url = f"{api_url}/login"
        status, payload = post_json(
            url,
            data={"username": username, "password": password}, # Often form-data or json
            # ZenML v1 login endpoint might vary.
            # Some versions use /api/v1/login with x-www-form-urlencoded
            # For simplicity, we assume the user provides a TOKEN if login is complex.
            # But let's try basic JSON login if supported.
        )
        # ZenML often uses OAuth2 /token endpoint.
        # If this fails, we recommend user to provide the token directly.
        pass

    # If credential is provided but we can't login easily, assume it's a token
    return credential


def creds_valid(credential: str, api_url: str) -> bool:
    token = _get_token(credential, api_url)
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        # Check /health or /info or /workspaces
        status, _ = get_json(f"{api_url}/workspaces", headers=headers)
        return status == 200
    except Exception:
        return False


def list_projects(credential: str, api_url: str) -> list[dict]:
    token = _get_token(credential, api_url)
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # ZenML uses "workspaces" as projects
    status, payload = get_json(f"{api_url}/workspaces", headers=headers)
    if status != 200:
        raise RuntimeError(f"ZenML returned HTTP {status}")
        
    out = []
    # Payload usually: {"items": [...], "total": ...}
    items = payload.get("items", []) if isinstance(payload, dict) else []
    
    for item in items:
        if isinstance(item, dict):
            out.append({
                "id": str(item.get("id", "")),
                "name": str(item.get("name", "")),
                "created": str(item.get("created", "")),
            })
    return out


def list_stacks(credential: str, api_url: str, project_id: str = "") -> list[dict]:
    token = _get_token(credential, api_url)
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    url = f"{api_url}/stacks"
    if project_id:
        url += f"?workspace_id={project_id}"
        
    status, payload = get_json(url, headers=headers)
    if status != 200:
        return []
        
    out = []
    items = payload.get("items", []) if isinstance(payload, dict) else []
    
    for item in items:
        if isinstance(item, dict):
            out.append({
                "id": str(item.get("id", "")),
                "name": str(item.get("name", "")),
                "components": len(item.get("components", {})),
            })
    return out
