from __future__ import annotations

from dataclasses import dataclass

from pymlokit.utils.http import get_json, request


@dataclass(frozen=True)
class BigMLCreds:
    username: str
    api_key: str


def _parse_creds(credential: str) -> BigMLCreds:
    parts = credential.split(";")
    if len(parts) < 2:
        raise ValueError("Invalid credential format. Expected username;apiKey")
    return BigMLCreds(username=parts[0], api_key=parts[1])


def creds_valid(credential: str, base_url: str = "https://bigml.io") -> bool:
    c = _parse_creds(credential)
    url = f"{base_url}/source?username={c.username}&api_key={c.api_key}"
    resp = request("GET", url, headers={"Content-Type": "application/json"})
    return resp.status == 200


def _objects(payload: object) -> list[dict]:
    if isinstance(payload, dict):
        objs = payload.get("objects")
        if isinstance(objs, list):
            return [o for o in objs if isinstance(o, dict)]
    if isinstance(payload, list):
        return [o for o in payload if isinstance(o, dict)]
    return []


def list_projects(credential: str, base_url: str = "https://bigml.io") -> list[dict]:
    c = _parse_creds(credential)
    status, payload = get_json(f"{base_url}/project?username={c.username}&api_key={c.api_key}")
    if status != 200:
        raise RuntimeError(f"BigML returned HTTP {status}")
    out = []
    for o in _objects(payload):
        rid = str(o.get("resource", "") or "")
        project_id = rid.split("/", 1)[1] if "/" in rid else rid
        visibility = "Private" if bool(o.get("private", False)) else "Public"
        out.append(
            {
                "name": o.get("name", ""),
                "creator": o.get("creator", ""),
                "visibility": visibility,
                "created": o.get("created", ""),
                "id": project_id,
            }
        )
    seen = set()
    deduped = []
    for p in out:
        pid = p.get("id", "")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        deduped.append(p)
    return deduped


def list_models(credential: str, base_url: str = "https://bigml.io") -> list[dict]:
    c = _parse_creds(credential)
    status, payload = get_json(f"{base_url}/model?username={c.username}&api_key={c.api_key}")
    if status != 200:
        raise RuntimeError(f"BigML returned HTTP {status}")
    out = []
    for o in _objects(payload):
        rid = str(o.get("resource", "") or "")
        model_id = rid.split("/", 1)[1] if "/" in rid else rid
        visibility = "Private" if bool(o.get("private", False)) else "Public"
        out.append(
            {
                "name": o.get("name", ""),
                "creator": o.get("creator", ""),
                "visibility": visibility,
                "created": o.get("created", ""),
                "updated": o.get("updated", ""),
                "id": model_id,
            }
        )
    seen = set()
    deduped = []
    for m in out:
        mid = m.get("id", "")
        if not mid or mid in seen:
            continue
        seen.add(mid)
        deduped.append(m)
    return deduped


def list_datasets(credential: str, base_url: str = "https://bigml.io") -> list[dict]:
    c = _parse_creds(credential)
    status, payload = get_json(f"{base_url}/dataset?username={c.username}&api_key={c.api_key}")
    if status != 200:
        raise RuntimeError(f"BigML returned HTTP {status}")
    out = []
    for o in _objects(payload):
        rid = str(o.get("resource", "") or "")
        dataset_id = rid.split("/", 1)[1] if "/" in rid else rid
        visibility = "Private" if bool(o.get("private", False)) else "Public"
        out.append(
            {
                "name": o.get("name", ""),
                "visibility": visibility,
                "created": o.get("created", ""),
                "updated": o.get("updated", ""),
                "id": dataset_id,
            }
        )
    seen = set()
    deduped = []
    for d in out:
        did = d.get("id", "")
        if not did or did in seen:
            continue
        seen.add(did)
        deduped.append(d)
    return deduped


def download_model_pmml(credential: str, model_id: str) -> str:
    c = _parse_creds(credential)
    url = f"https://bigml.io/model/{model_id}?username={c.username}&api_key={c.api_key}&pmml=yes"
    status, payload = get_json(url)
    if status != 200:
        raise RuntimeError(f"BigML returned HTTP {status}")
    if isinstance(payload, dict):
        pmml = payload.get("pmml")
        return "" if pmml is None else str(pmml)
    return ""


def download_dataset_bytes(credential: str, dataset_id: str) -> bytes:
    c = _parse_creds(credential)
    url = f"https://bigml.io/dataset/{dataset_id}/download?username={c.username}&api_key={c.api_key}"
    resp = request("GET", url, headers={"Content-Type": "application/json"})
    if resp.status != 200:
        raise RuntimeError(f"BigML returned HTTP {resp.status}")
    return resp.body
 
