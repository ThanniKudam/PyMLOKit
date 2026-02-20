from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from pymlokit.utils.http import get_json, request


@dataclass(frozen=True)
class MLflowCreds:
    username: str
    password: str


def _parse_creds(credential: str) -> MLflowCreds:
    parts = credential.split(";")
    if len(parts) < 2:
        raise ValueError("Invalid credential format. Expected username;password")
    return MLflowCreds(username=parts[0], password=parts[1])


def _auth_header(credential: str) -> str:
    c = _parse_creds(credential)
    raw = f"{c.username}:{c.password}".encode("utf-8")
    token = base64.b64encode(raw).decode("utf-8")
    return f"Basic {token}"


def creds_valid(credential: str, url: str) -> bool:
    status, _ = get_json(
        f"{url}/api/2.0/mlflow/model-versions/search",
        headers={"Authorization": _auth_header(credential)},
    )
    return status == 200


def list_models(credential: str, url: str) -> list[dict]:
    status, payload = get_json(
        f"{url}/api/2.0/mlflow/model-versions/search",
        headers={"Authorization": _auth_header(credential)},
    )
    if status != 200:
        raise RuntimeError(f"MLflow returned HTTP {status}")
    models = []
    if isinstance(payload, dict) and isinstance(payload.get("model_versions"), list):
        for mv in payload["model_versions"]:
            if not isinstance(mv, dict):
                continue
            models.append(
                {
                    "name": mv.get("name", ""),
                    "version": mv.get("version", ""),
                    "status": mv.get("status", ""),
                    "description": mv.get("description", ""),
                    "artifact_location": mv.get("source", ""),
                    "run_id": mv.get("run_id", ""),
                }
            )
    seen = set()
    deduped = []
    for m in models:
        name = str(m.get("name", "") or "")
        if not name or name in seen:
            continue
        seen.add(name)
        deduped.append(m)
    return deduped


def get_artifact_root_dir(credential: str, url: str, run_id: str) -> str:
    status, payload = get_json(
        f"{url}/api/2.0/mlflow/artifacts/list?run_id={quote(run_id)}",
        headers={"Authorization": _auth_header(credential)},
    )
    if status != 200:
        raise RuntimeError(f"MLflow returned HTTP {status}")
    if isinstance(payload, dict) and isinstance(payload.get("files"), list):
        for f in payload["files"]:
            if isinstance(f, dict) and f.get("path"):
                return str(f["path"])
    return ""


def list_artifacts_recursive(credential: str, url: str, run_id: str, path: str) -> list[dict]:
    out: list[dict] = []
    queue = [path]
    while queue:
        p = queue.pop(0)
        q = f"{url}/api/2.0/mlflow/artifacts/list?run_id={quote(run_id)}&path={quote(p)}"
        status, payload = get_json(q, headers={"Authorization": _auth_header(credential)})
        if status != 200:
            raise RuntimeError(f"MLflow returned HTTP {status}")
        if not (isinstance(payload, dict) and isinstance(payload.get("files"), list)):
            continue
        for f in payload["files"]:
            if not isinstance(f, dict):
                continue
            fp = str(f.get("path", "") or "")
            is_dir = bool(f.get("is_dir", False))
            if not fp:
                continue
            if is_dir:
                queue.append(fp)
            else:
                out.append({"path": fp})
    return out


def download_artifact(credential: str, url: str, run_id: str, path: str) -> bytes:
    q = f"{url}/get-artifact?path={quote(path)}&run_id={quote(run_id)}"
    resp = request("GET", q, headers={"Authorization": _auth_header(credential)})
    if resp.status != 200:
        raise RuntimeError(f"MLflow returned HTTP {resp.status}")
    return resp.body
 
