from __future__ import annotations

from pymlokit.utils.http import get_json


def _get_headers(credential: str) -> dict[str, str]:
    # Credential format: token or "Bearer token"
    if not credential:
        return {}
    if credential.lower().startswith("bearer "):
        return {"Authorization": credential}
    return {"Authorization": f"Bearer {credential}"}


def creds_valid(credential: str, api_url: str) -> bool:
    headers = _get_headers(credential)
    try:
        # Check /apis/v1beta1/pipelines or similar
        status, _ = get_json(f"{api_url}/apis/v1beta1/pipelines", headers=headers)
        return status == 200
    except Exception:
        # Try v2beta1
        try:
            status, _ = get_json(f"{api_url}/apis/v2beta1/pipelines", headers=headers)
            return status == 200
        except Exception:
            return False


def list_pipelines(credential: str, api_url: str) -> list[dict]:
    headers = _get_headers(credential)
    
    # Try v1beta1
    url = f"{api_url}/apis/v1beta1/pipelines"
    status, payload = get_json(url, headers=headers)
    
    if status != 200:
        # Try v2beta1
        url = f"{api_url}/apis/v2beta1/pipelines"
        status, payload = get_json(url, headers=headers)
        if status != 200:
            raise RuntimeError(f"Kubeflow returned HTTP {status}")

    out = []
    # KFP usually returns {"pipelines": [...]} or {"items": [...]}?
    # v1beta1: {"pipelines": [...]}
    pipelines = payload.get("pipelines", []) if isinstance(payload, dict) else []
    
    for p in pipelines:
        if isinstance(p, dict):
            out.append({
                "id": str(p.get("id", "")),
                "name": str(p.get("name", "")),
                "created_at": str(p.get("created_at", "")),
                "description": str(p.get("description", "")),
            })
    return out


def list_runs(credential: str, api_url: str) -> list[dict]:
    headers = _get_headers(credential)
    
    # Try v1beta1
    url = f"{api_url}/apis/v1beta1/runs"
    status, payload = get_json(url, headers=headers)
    
    if status != 200:
        # Try v2beta1
        url = f"{api_url}/apis/v2beta1/runs"
        status, payload = get_json(url, headers=headers)
        if status != 200:
            return []

    out = []
    runs = payload.get("runs", []) if isinstance(payload, dict) else []
    
    for r in runs:
        if isinstance(r, dict):
            out.append({
                "id": str(r.get("id", "")),
                "name": str(r.get("name", "")),
                "created_at": str(r.get("created_at", "")),
                "status": str(r.get("status", "")),
                "pipeline_spec": str(r.get("pipeline_spec", {}).get("pipeline_id", "")),
            })
    return out
