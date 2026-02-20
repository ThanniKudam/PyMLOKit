from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from pymlokit.utils.http import get_json, post_json, request


@dataclass(frozen=True)
class VertexProject:
    name: str
    project_id: str
    project_number: str
    lifecycle_state: str
    create_time: str


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def creds_valid(token: str) -> bool:
    status, _ = get_json(
        "https://cloudresourcemanager.googleapis.com/v1/projects?alt=json&filter=lifecycleState%3AACTIVE&pageSize=500",
        headers=_auth_headers(token),
    )
    return status == 200


def list_projects(token: str) -> list[VertexProject]:
    status, payload = get_json(
        "https://cloudresourcemanager.googleapis.com/v1/projects?alt=json&filter=lifecycleState%3AACTIVE&pageSize=500",
        headers=_auth_headers(token),
    )
    if status != 200:
        raise RuntimeError(f"VertexAI returned HTTP {status}")
    out: list[VertexProject] = []
    if isinstance(payload, dict) and isinstance(payload.get("projects"), list):
        for p in payload["projects"]:
            if not isinstance(p, dict):
                continue
            out.append(
                VertexProject(
                    name=str(p.get("name", "") or ""),
                    project_id=str(p.get("projectId", "") or ""),
                    project_number=str(p.get("projectNumber", "") or ""),
                    lifecycle_state=str(p.get("lifecycleState", "") or ""),
                    create_time=str(p.get("createTime", "") or ""),
                )
            )
    return out


def list_regions(token: str, project: str) -> list[str]:
    status, payload = get_json(
        f"https://apigateway.googleapis.com/v1/projects/{quote(project)}/locations",
        headers=_auth_headers(token),
    )
    if status != 200:
        raise RuntimeError(f"VertexAI returned HTTP {status}")
    regions: list[str] = []
    if isinstance(payload, dict) and isinstance(payload.get("locations"), list):
        for loc in payload["locations"]:
            if not isinstance(loc, dict):
                continue
            name = str(loc.get("name", "") or "")
            if name and "/" in name:
                regions.append(name.split("/")[-1])
    seen = set()
    out = []
    for r in regions:
        if r and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def list_models(token: str, region: str, project: str) -> list[dict]:
    status, payload = get_json(
        f"https://{region}-aiplatform.googleapis.com/v1/projects/{quote(project)}/locations/{quote(region)}/models",
        headers=_auth_headers(token),
    )
    if status != 200:
        return []
    export_allow = {"tflite", "edgetpu-tflite", "tf-saved-model", "tf-js", "core-ml", "custom-trained"}
    out: list[dict] = []
    if isinstance(payload, dict) and isinstance(payload.get("models"), list):
        for m in payload["models"]:
            if not isinstance(m, dict):
                continue
            full_name = str(m.get("name", "") or "")
            model_id = full_name.split("/")[-1] if full_name else ""
            display = str(m.get("displayName", "") or "")
            create_time = str(m.get("createTime", "") or "")
            update_time = str(m.get("updateTime", "") or "")
            source_type = ""
            if isinstance(m.get("sourceInfo"), dict):
                source_type = str(m["sourceInfo"].get("sourceType", "") or "")
            export_fmt = ""
            sef = m.get("supportedExportFormats")
            if isinstance(sef, list):
                for f in sef:
                    if isinstance(f, dict):
                        fid = str(f.get("id", "") or "")
                        if fid.lower() in export_allow:
                            export_fmt = fid
                            break
            if model_id and display and create_time and update_time and source_type and export_fmt:
                out.append(
                    {
                        "id": model_id,
                        "display_name": display,
                        "create_time": create_time,
                        "update_time": update_time,
                        "source_type": source_type,
                        "exportable_format": export_fmt,
                        "region": region,
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


def list_datasets(token: str, region: str, project: str) -> list[dict]:
    status, payload = get_json(
        f"https://{region}-aiplatform.googleapis.com/v1/projects/{quote(project)}/locations/{quote(region)}/datasets",
        headers=_auth_headers(token),
    )
    if status != 200:
        return []
    out: list[dict] = []
    if isinstance(payload, dict) and isinstance(payload.get("datasets"), list):
        for d in payload["datasets"]:
            if not isinstance(d, dict):
                continue
            full_name = str(d.get("name", "") or "")
            dataset_id = full_name.split("/")[-1] if full_name else ""
            display = str(d.get("displayName", "") or "")
            create_time = str(d.get("createTime", "") or "")
            update_time = str(d.get("updateTime", "") or "")
            uri = str(d.get("metadata"), "" or "")
            if isinstance(d.get("metadata"), dict):
                uri = str(d["metadata"].get("inputConfig", {}).get("gcsSource", {}).get("uri", "") or "")
            if dataset_id and display and create_time and update_time and uri:
                out.append(
                    {
                        "id": dataset_id,
                        "display_name": display,
                        "create_time": create_time,
                        "update_time": update_time,
                        "uri": uri,
                        "region": region,
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


def list_buckets(token: str, project: str) -> list[str]:
    url = (
        "https://storage.googleapis.com/storage/v1/b?alt=json&fields=items%2Fname%2CnextPageToken"
        f"&maxResults=1000&project={quote(project)}&projection=noAcl"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200:
        return []
    buckets = []
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        for it in payload["items"]:
            if isinstance(it, dict) and it.get("name"):
                buckets.append(str(it["name"]))
    return buckets


def export_model(token: str, region: str, project: str, model_id: str, bucket: str, export_format: str) -> str:
    url = (
        f"https://{region}-aiplatform.googleapis.com/v1/projects/{quote(project)}/locations/{quote(region)}/models/"
        f"{quote(model_id)}:export"
    )
    payload = {
        "outputConfig": {
            "exportFormatId": export_format,
            "artifactDestination": {"outputUriPrefix": f"gs://{bucket}"},
        }
    }
    status, resp = post_json(url, payload, headers=_auth_headers(token))
    if status != 200:
        return ""
    if isinstance(resp, dict):
        out_uri = resp.get("artifactOutputUri")
        return "" if out_uri is None else str(out_uri)
    return ""


def list_objects(token: str, bucket: str, prefix: str) -> list[str]:
    url = (
        f"https://storage.googleapis.com/storage/v1/b/{quote(bucket)}/o?alt=json&prefix={quote(prefix)}"
        "&fields=items%2Fname%2CnextPageToken&maxResults=1000&projection=noAcl"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200:
        return []
    names = []
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        for it in payload["items"]:
            if isinstance(it, dict) and it.get("name"):
                names.append(str(it["name"]))
    return names


def get_media_link(token: str, bucket: str, object_name: str) -> str:
    url = f"https://storage.googleapis.com/storage/v1/b/{quote(bucket)}/o/{quote(object_name, safe='')}"
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200:
        return ""
    if isinstance(payload, dict) and payload.get("mediaLink"):
        return str(payload["mediaLink"])
    return ""


def download_media_link(token: str, media_link: str) -> bytes:
    resp = request("GET", media_link, headers=_auth_headers(token))
    if resp.status != 200:
        raise RuntimeError(f"GCS returned HTTP {resp.status}")
    return resp.body


def parse_gs_uri(gs_uri: str) -> tuple[str, str]:
    s = gs_uri.strip()
    if not s.startswith("gs://"):
        raise ValueError("Expected gs:// URI")
    rest = s[5:]
    bucket, _, path = rest.partition("/")
    return bucket, path


def wait_for_export(seconds: float = 15.0) -> None:
    time.sleep(seconds)
 
