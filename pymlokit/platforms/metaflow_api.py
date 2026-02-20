from __future__ import annotations

from pymlokit.utils.http import get_json


def creds_valid(service_url: str) -> bool:
    # Metaflow service often has a /ping endpoint
    try:
        status, _ = get_json(f"{service_url}/ping")
        return status == 200
    except Exception:
        # Fallback to listing flows
        try:
            status, _ = get_json(f"{service_url}/flows")
            return status == 200
        except Exception:
            return False


def list_flows(service_url: str) -> list[dict]:
    status, payload = get_json(f"{service_url}/flows")
    if status != 200:
        raise RuntimeError(f"Metaflow returned HTTP {status}")
    
    # Payload is usually a list of strings (flow ids) or objects depending on version
    # Standard metadata service returns list of objects usually?
    # Actually, standard OSS metadata service returns JSON list of flow IDs: ["flow1", "flow2"]
    # Or `[{"flow_id": "..."}]`?
    # Let's assume list of strings or dicts.
    
    out = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, str):
                out.append({"id": item})
            elif isinstance(item, dict):
                out.append({
                    "id": item.get("flow_id", "") or item.get("id", ""),
                    "created_at": str(item.get("created_at", "") or item.get("ts_epoch", "")),
                })
    return out


def list_runs(service_url: str, flow_id: str) -> list[dict]:
    status, payload = get_json(f"{service_url}/flows/{flow_id}/runs")
    if status != 200:
        return []
        
    out = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                out.append({
                    "id": item.get("run_number", "") or item.get("run_id", ""),
                    "user": item.get("user_name", "") or item.get("user", ""),
                    "created_at": str(item.get("ts_epoch", "")),
                    "status": "completed" if item.get("system_tags", []) else "unknown" # simplified
                })
            elif isinstance(item, str):
                out.append({"id": item})
    return out
