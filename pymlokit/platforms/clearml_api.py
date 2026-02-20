from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

from pymlokit.utils.http import get_json, post_json, request


@dataclass(frozen=True)
class ClearMLCreds:
    access_key: str
    secret_key: str


def _parse_creds(credential: str) -> ClearMLCreds:
    parts = credential.split(";")
    if len(parts) < 2:
        raise ValueError("Invalid credential format. Expected ACCESS_KEY;SECRET_KEY")
    return ClearMLCreds(access_key=parts[0], secret_key=parts[1])


def _get_token(credential: str, api_url: str) -> str:
    c = _parse_creds(credential)
    raw = f"{c.access_key}:{c.secret_key}".encode("utf-8")
    auth = base64.b64encode(raw).decode("utf-8")
    
    url = f"{api_url}/auth.login"
    status, payload = post_json(
        url,
        {},
        headers={"Authorization": f"Basic {auth}"},
    )
    
    if status != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"ClearML Login Failed. Status: {status}")
        
    data = payload.get("data")
    if isinstance(data, dict):
        return str(data.get("token", "") or "")
    return ""


def creds_valid(credential: str, api_url: str) -> bool:
    try:
        token = _get_token(credential, api_url)
        return bool(token)
    except Exception:
        return False


def list_projects(credential: str, api_url: str) -> list[dict]:
    token = _get_token(credential, api_url)
    if not token:
        raise RuntimeError("Failed to authenticate with ClearML")
        
    status, payload = post_json(
        f"{api_url}/projects.get_all",
        {"order_by": ["last_update"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    if status != 200:
        raise RuntimeError(f"ClearML returned HTTP {status}")
        
    out = []
    data = payload.get("data") if isinstance(payload, dict) else {}
    projects = data.get("projects") if isinstance(data, dict) else []
    
    if isinstance(projects, list):
        for p in projects:
            if not isinstance(p, dict):
                continue
            out.append({
                "id": str(p.get("id", "")),
                "name": str(p.get("name", "")),
                "created": str(p.get("created", "")),
                "last_update": str(p.get("last_update", "")),
                "stats": p.get("stats", {}),
            })
    return out


def list_models(credential: str, api_url: str, project_id: str = "") -> list[dict]:
    token = _get_token(credential, api_url)
    if not token:
        raise RuntimeError("Failed to authenticate with ClearML")
        
    body = {"order_by": ["-last_update"], "page_size": 100}
    if project_id:
        body["project"] = [project_id]
        
    status, payload = post_json(
        f"{api_url}/models.get_all",
        body,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    if status != 200:
        raise RuntimeError(f"ClearML returned HTTP {status}")
        
    out = []
    data = payload.get("data") if isinstance(payload, dict) else {}
    models = data.get("models") if isinstance(data, dict) else []
    
    if isinstance(models, list):
        for m in models:
            if not isinstance(m, dict):
                continue
            out.append({
                "id": str(m.get("id", "")),
                "name": str(m.get("name", "")),
                "uri": str(m.get("uri", "")),
                "created": str(m.get("created", "")),
                "project": str(m.get("project", "")),
                "framework": str(m.get("framework", "")),
                "labels": m.get("labels", {}),
            })
    return out


def list_datasets(credential: str, api_url: str, project_id: str = "") -> list[dict]:
    # ClearML Datasets are typically Tasks with type "data_processing" or created via clearml-data
    # We will search for tasks with type "data_processing" or specific tags.
    token = _get_token(credential, api_url)
    if not token:
        raise RuntimeError("Failed to authenticate with ClearML")
        
    body = {
        "type": ["data_processing"], 
        "order_by": ["-last_update"], 
        "page_size": 100
    }
    if project_id:
        body["project"] = [project_id]
        
    status, payload = post_json(
        f"{api_url}/tasks.get_all",
        body,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    if status != 200:
        raise RuntimeError(f"ClearML returned HTTP {status}")
        
    out = []
    data = payload.get("data") if isinstance(payload, dict) else {}
    tasks = data.get("tasks") if isinstance(data, dict) else []
    
    if isinstance(tasks, list):
        for t in tasks:
            if not isinstance(t, dict):
                continue
            out.append({
                "id": str(t.get("id", "")),
                "name": str(t.get("name", "")),
                "created": str(t.get("created", "")),
                "status": str(t.get("status", "")),
                "project": str(t.get("project", "")),
                "type": str(t.get("type", "")),
            })
    return out


def get_model_url(credential: str, api_url: str, model_id: str) -> str:
    token = _get_token(credential, api_url)
    if not token:
        raise RuntimeError("Failed to authenticate with ClearML")
        
    status, payload = post_json(
        f"{api_url}/models.get_by_id",
        {"models": [model_id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    if status != 200:
        raise RuntimeError(f"ClearML returned HTTP {status}")
        
    data = payload.get("data") if isinstance(payload, dict) else {}
    models = data.get("models") if isinstance(data, dict) else []
    if isinstance(models, list) and len(models) > 0:
        m = models[0]
        if isinstance(m, dict):
            return str(m.get("uri", "") or "")
    return ""


def download_url_bytes(url: str) -> bytes:
    # If it's a local file path (file://), we can't download it over HTTP
    # If it's s3:// or gs://, we need specialized handling, but for now we assume HTTP(S)
    if url.startswith("file://") or url.startswith("/"):
        raise ValueError(f"Cannot download local file URL: {url}")
    if url.startswith("s3://") or url.startswith("gs://") or url.startswith("azure://"):
        raise ValueError(f"Cloud storage URL not supported directly via HTTP download: {url}")
        
    resp = request("GET", url)
    if resp.status != 200:
        raise RuntimeError(f"Download returned HTTP {resp.status}")
    return resp.body
