from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pymlokit.utils.http import get_json, request


@dataclass(frozen=True)
class PalantirCreds:
    token: str
    tenant: str
    apprid: str


def parse_creds(credential: str) -> PalantirCreds:
    parts = credential.split(";")
    if len(parts) < 2:
        raise ValueError("Invalid credential format. Expected token;tenant[;apprid]")
    token = parts[0]
    tenant = parts[1]
    apprid = parts[2] if len(parts) >= 3 else ""
    return PalantirCreds(token=token, tenant=tenant, apprid=apprid)


def _auth_headers(creds: PalantirCreds) -> dict[str, str]:
    return {"Authorization": f"Bearer {creds.token}"}


def creds_valid(credential: str) -> bool:
    c = parse_creds(credential)
    status, _ = get_json(f"https://{c.tenant}/api/v1/ontologies", headers=_auth_headers(c))
    return status == 200


def _get_data_list(payload: Any) -> list[dict]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return [x for x in payload["data"] if isinstance(x, dict)]
    return []


def list_spaces(credential: str) -> list[dict]:
    c = parse_creds(credential)
    status, payload = get_json(f"https://{c.tenant}/api/v2/filesystem/spaces?preview=true", headers=_auth_headers(c))
    if status != 200:
        return []
    spaces = []
    for s in _get_data_list(payload):
        spaces.append({"displayName": s.get("displayName", ""), "rid": s.get("rid", "")})
    return spaces


def folder_children(credential: str, folder_rid: str) -> list[dict]:
    c = parse_creds(credential)
    status, payload = get_json(
        f"https://{c.tenant}/api/v2/filesystem/folders/{folder_rid}/children?preview=true", headers=_auth_headers(c)
    )
    if status != 200:
        return []
    items = []
    for it in _get_data_list(payload):
        items.append(
            {
                "displayName": it.get("displayName", ""),
                "rid": it.get("rid", ""),
                "type": it.get("type", ""),
                "createdTime": it.get("createdTime", ""),
                "updatedTime": it.get("updatedTime", ""),
                "parentFolderRid": it.get("parentFolderRid", ""),
            }
        )
    return items


def folder_info(credential: str, folder_rid: str) -> dict | None:
    c = parse_creds(credential)
    status, payload = get_json(
        f"https://{c.tenant}/api/v2/filesystem/folders/{folder_rid}?preview=true", headers=_auth_headers(c)
    )
    if status != 200 or not isinstance(payload, dict):
        return None
    return {"displayName": payload.get("displayName", ""), "path": payload.get("path", ""), "type": payload.get("type", "")}


def _is_example_content(item_name: str, item_path: str) -> bool:
    return ("AIP Now Ontology" in item_name) or ("[Example]" in item_name) or ("[Example]" in item_path)


def find_datasets_recursively(credential: str, folder_rid: str, path: str, max_depth: int, current_depth: int) -> list[dict]:
    if current_depth >= max_depth:
        return []
    datasets: list[dict] = []
    items = folder_children(credential, folder_rid)
    for it in items:
        display = str(it.get("displayName", "") or "")
        rid = str(it.get("rid", "") or "")
        typ = str(it.get("type", "") or "")
        item_path = f"{path}/{display}" if path else display
        if not rid:
            continue
        if _is_example_content(display, item_path):
            continue
        if typ == "FOUNDRY_DATASET":
            datasets.append(
                {
                    "dataset_name": display,
                    "type": typ,
                    "date_created": str(it.get("createdTime", "") or "Unknown"),
                    "date_updated": str(it.get("updatedTime", "") or "Unknown"),
                    "dataset_rid": rid,
                    "path": item_path,
                    "parent_folder_rid": str(it.get("parentFolderRid", "") or folder_rid),
                }
            )
        elif typ in {"FOLDER", "PROJECT", "SPACE", "COMPASS_FOLDER"}:
            datasets.extend(find_datasets_recursively(credential, rid, item_path, max_depth, current_depth + 1))
    return datasets


def list_datasets(credential: str) -> list[dict]:
    c = parse_creds(credential)
    datasets: list[dict] = []

    if c.apprid:
        info = folder_info(credential, c.apprid)
        folder_name = str((info or {}).get("displayName", "") or "")
        datasets = find_datasets_recursively(credential, c.apprid, folder_name, 3, 0)

    if not datasets:
        spaces = list_spaces(credential)
        for s in spaces:
            rid = str(s.get("rid", "") or "")
            name = str(s.get("displayName", "") or "")
            if not rid:
                continue
            datasets.extend(find_datasets_recursively(credential, rid, name, 4, 0))

    seen = set()
    out = []
    for d in datasets:
        rid = str(d.get("dataset_rid", "") or "")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        out.append(d)
    return out


def download_dataset_csv(credential: str, dataset_rid: str) -> bytes:
    c = parse_creds(credential)
    url = f"https://{c.tenant}/api/v2/datasets/{dataset_rid}/readTable?format=csv"
    resp = request("GET", url, headers=_auth_headers(c))
    if resp.status != 200:
        raise RuntimeError(f"Palantir returned HTTP {resp.status}")
    return resp.body


def get_dataset_details(credential: str, dataset_rid: str) -> str:
    c = parse_creds(credential)
    status, payload = get_json(f"https://{c.tenant}/api/v2/datasets/{dataset_rid}", headers=_auth_headers(c))
    if status != 200:
        return ""
    return json.dumps(payload) if payload is not None else ""


def upload_dataset(credential: str, dataset_name: str, file_bytes: bytes, original_file_name: str) -> str:
    c = parse_creds(credential)
    create_url = f"https://{c.tenant}/api/v2/datasets"
    payload = {"name": dataset_name, "parentFolderRid": (c.apprid if c.apprid else "")}
    resp = request(
        "POST",
        create_url,
        headers={"Content-Type": "application/json", **_auth_headers(c)},
        body=json.dumps(payload).encode("utf-8"),
    )
    if resp.status not in (200, 201):
        raise RuntimeError(f"Palantir returned HTTP {resp.status}")
    created = json.loads(resp.body.decode("utf-8", errors="replace")) if resp.body else {}
    dataset_rid = str(created.get("rid", "") or "")
    if not dataset_rid:
        raise RuntimeError("Failed to create dataset or parse dataset RID")

    boundary = f"----WebKitFormBoundary{int(__import__('time').time() * 1000):x}"
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{original_file_name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = header + file_bytes + footer

    upload_url = f"https://{c.tenant}/api/v2/datasets/{dataset_rid}/files"
    up_resp = request(
        "POST",
        upload_url,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", **_auth_headers(c)},
        body=body,
    )
    if up_resp.status not in (200, 201):
        raise RuntimeError(f"Palantir returned HTTP {up_resp.status}")
    return dataset_rid
 
