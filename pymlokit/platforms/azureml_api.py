from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from pymlokit.utils.azure_storage import shared_key_authorization, storage_headers_common
from pymlokit.utils.http import get_json, request


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def creds_valid(token: str) -> bool:
    status, _ = get_json(
        "https://management.azure.com/subscriptions?api-version=2022-12-01",
        headers=_auth_headers(token),
    )
    return status == 200


def list_subscriptions(token: str) -> list[dict]:
    status, payload = get_json(
        "https://management.azure.com/subscriptions?api-version=2022-12-01",
        headers=_auth_headers(token),
    )
    if status != 200:
        return []
    out = []
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        for s in payload["value"]:
            if not isinstance(s, dict):
                continue
            out.append(
                {
                    "display_name": s.get("displayName", ""),
                    "id": s.get("subscriptionId", ""),
                    "state": s.get("state", ""),
                }
            )
    return out


def list_workspaces(token: str, subscription_id: str) -> list[dict]:
    status, payload = get_json(
        f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.MachineLearningServices/workspaces?api-version=2023-10-01",
        headers=_auth_headers(token),
    )
    if status != 200:
        return []
    out = []
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        for w in payload["value"]:
            if not isinstance(w, dict):
                continue
            props = w.get("properties") if isinstance(w.get("properties"), dict) else {}
            ws_id = str(props.get("workspaceId", "") or "")
            created_by = str(props.get("createdBy", "") or "")
            creation_time = str(props.get("creationTime", "") or "")
            tracking = str(props.get("mlflowTrackingUri", "") or "")
            region = ""
            if tracking:
                parts = tracking.split("/")
                if len(parts) >= 3:
                    region = parts[2].replace(".api.azureml.ms", "")
            rid = str(w.get("id", "") or "")
            resource_group = rid.split("/")[4] if rid and len(rid.split("/")) > 4 else ""
            name = str(w.get("name", "") or "")
            if not name and rid:
                sp = rid.split("/")
                name = sp[-1] if sp else ""
            if ws_id and name and region and resource_group:
                out.append(
                    {
                        "name": name,
                        "workspace_id": ws_id,
                        "region": region,
                        "resource_group": resource_group,
                        "creation_time": creation_time,
                        "created_by": created_by,
                    }
                )
    return out


def list_models(token: str, subscription_id: str, region: str, resource_group: str, workspace: str) -> list[dict]:
    base = (
        f"https://{region}.modelmanagement.azureml.net/modelmanagement/v1.0/subscriptions/{subscription_id}/resourceGroups/"
        f"{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace}/models?api-version=2023-10-01"
    )
    next_link = base
    out: list[dict] = []
    while next_link:
        status, payload = get_json(next_link, headers=_auth_headers(token))
        if status != 200 or not isinstance(payload, dict):
            break
        vals = payload.get("value")
        if isinstance(vals, list):
            for m in vals:
                if not isinstance(m, dict):
                    continue
                mid = str(m.get("id", "") or "")
                name = str(m.get("name", "") or "")
                model_type = str(m.get("modelType", "") or "")
                created = str(m.get("createdTime", "") or "")
                modified = str(m.get("modifiedTime", "") or "")
                asset_id = ""
                url = str(m.get("url", "") or "")
                if url and "/" in url:
                    parts = url.split("/")
                    if len(parts) > 3:
                        asset_id = parts[3]
                if mid:
                    out.append(
                        {
                            "id": mid,
                            "name": name,
                            "model_type": model_type,
                            "created_time": created,
                            "modified_time": modified,
                            "asset_id": asset_id,
                        }
                    )
        next_link = str(payload.get("nextLink", "") or "")
    seen = set()
    deduped = []
    for m in out:
        mid = m.get("id", "")
        if not mid or mid in seen:
            continue
        seen.add(mid)
        deduped.append(m)
    return deduped


def get_model(token: str, subscription_id: str, region: str, resource_group: str, workspace: str, model_id: str) -> dict | None:
    url = (
        f"https://{region}.modelmanagement.azureml.net/modelmanagement/v1.0/subscriptions/{subscription_id}/resourceGroups/"
        f"{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace}/models/{model_id}?api-version=2023-10-01"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return None
    asset_id = ""
    urlv = str(payload.get("url", "") or "")
    if urlv and "/" in urlv:
        parts = urlv.split("/")
        if len(parts) > 3:
            asset_id = parts[3]
    return {
        "id": payload.get("id", ""),
        "name": payload.get("name", ""),
        "model_type": payload.get("modelType", ""),
        "created_time": payload.get("createdTime", ""),
        "modified_time": payload.get("modifiedTime", ""),
        "provisioning_state": payload.get("provisioningState", ""),
        "asset_id": asset_id,
    }


def get_asset_prefixes(token: str, subscription_id: str, region: str, resource_group: str, workspace: str, asset_id: str) -> list[str]:
    url = (
        f"https://{region}.modelmanagement.azureml.net/modelmanagement/v1.0/subscriptions/{subscription_id}/resourceGroups/"
        f"{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace}/assets/{asset_id}?api-version=2023-10-01"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return []
    prefixes = []
    artifacts = payload.get("artifacts")
    if isinstance(artifacts, list):
        for a in artifacts:
            if isinstance(a, dict):
                p = a.get("artifactPrefix")
                if p:
                    prefixes.append(str(p))
    return prefixes


def get_content_uris(
    token: str, subscription_id: str, region: str, resource_group: str, workspace: str, artifact_prefix: str
) -> list[str]:
    url = (
        f"https://{region}.experiments.azureml.net/artifact/v2.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace}/artifacts/prefix/contentinfo/{artifact_prefix}"
        f"?api-version=2023-10-01"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return []
    out = []
    v = payload.get("value")
    if isinstance(v, list):
        for it in v:
            if isinstance(it, dict) and it.get("contentUri"):
                out.append(str(it["contentUri"]))
    return out


def download_url_bytes(url: str) -> bytes:
    resp = request("GET", url, headers={"Content-Type": "application/json"})
    if resp.status != 200:
        raise RuntimeError(f"Download returned HTTP {resp.status}")
    return resp.body


def list_datasets(token: str, subscription_id: str, region: str, resource_group: str, workspace: str) -> list[dict]:
    url = (
        f"https://{region}.experiments.azureml.net/dataset/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace}/datasets?includeInvisible=false&pageSize=100"
        "&includeLatestDefinition=true"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return []
    out = []
    v = payload.get("value")
    if isinstance(v, list):
        for d in v:
            if not isinstance(d, dict):
                continue
            did = str(d.get("id", "") or "")
            name = str(d.get("name", "") or "")
            state = str(d.get("state", "") or "")
            data_type = str(d.get("dataType", "") or "")
            ds_name = str(d.get("datastoreName", "") or "")
            file_path = str(d.get("azureFilePath", "") or "")
            file_name = file_path.rsplit("/", 1)[-1] if file_path else ""
            if did:
                out.append(
                    {
                        "file_name": file_name,
                        "id": did,
                        "state": state,
                        "data_type": data_type,
                        "datastore_name": ds_name,
                        "azure_file_path": file_path,
                    }
                )
    return out


def get_dataset(token: str, subscription_id: str, region: str, resource_group: str, workspace: str, dataset_id: str) -> dict | None:
    url = (
        f"https://{region}.experiments.azureml.net/dataset/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace}/datasets/{dataset_id}?includeInvisible=false&pageSize=100"
        "&includeLatestDefinition=true"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return None
    return {
        "id": payload.get("id", ""),
        "name": payload.get("name", ""),
        "state": payload.get("state", ""),
        "data_type": payload.get("dataType", ""),
        "datastore_name": payload.get("datastoreName", ""),
        "azure_file_path": payload.get("azureFilePath", ""),
    }


def get_datastore(token: str, subscription_id: str, region: str, resource_group: str, workspace: str, name: str) -> dict | None:
    url = (
        f"https://{region}.experiments.azureml.net/datastore/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace}/datastores/{name}"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return None
    props = payload.get("properties") if isinstance(payload.get("properties"), dict) else payload
    return {
        "account_name": str(props.get("accountName", "") or ""),
        "container_name": str(props.get("containerName", "") or ""),
        "endpoint": str(props.get("endpoint", "") or ""),
        "credential": str(props.get("credential", "") or ""),
        "datastore_type": str(props.get("datastoreType", "") or ""),
        "name": str(props.get("name", "") or ""),
    }


def list_datastores(token: str, subscription_id: str, region: str, resource_group: str, workspace: str) -> list[dict]:
    url = (
        f"https://{region}.experiments.azureml.net/datastore/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/Microsoft.MachineLearningServices/workspaces/{workspace}/datastores?count=1000"
    )
    status, payload = get_json(url, headers=_auth_headers(token))
    if status != 200 or not isinstance(payload, dict):
        return []
    out = []
    v = payload.get("value")
    if isinstance(v, list):
        for ds in v:
            if not isinstance(ds, dict):
                continue
            props = ds.get("properties") if isinstance(ds.get("properties"), dict) else ds
            out.append(
                {
                    "account_name": str(props.get("accountName", "") or ""),
                    "container_name": str(props.get("containerName", "") or ""),
                    "endpoint": str(props.get("endpoint", "") or ""),
                    "credential": str(props.get("credential", "") or ""),
                    "datastore_type": str(props.get("datastoreType", "") or ""),
                    "name": str(props.get("name", "") or ""),
                }
            )
    return out


def download_blob(storage_account: str, storage_key_b64: str, container: str, relative_path: str) -> bytes:
    rel = relative_path.lstrip("/")
    url = f"https://{storage_account}.blob.core.windows.net/{container}/{rel}"
    now = datetime.now(timezone.utc)
    headers = {"Content-Type": "application/json", **storage_headers_common(now)}
    headers["Authorization"] = shared_key_authorization(
        storage_account_name=storage_account,
        storage_account_key_b64=storage_key_b64,
        now_utc=now,
        method="GET",
        url=url,
        headers=headers,
        content_length=None,
    )
    resp = request("GET", url, headers=headers)
    if resp.status != 200:
        raise RuntimeError(f"Azure Blob returned HTTP {resp.status}")
    return resp.body


def upload_blob(
    storage_account: str,
    storage_key_b64: str,
    container: str,
    relative_path: str,
    content: bytes,
) -> None:
    rel = relative_path.lstrip("/")
    url = f"https://{storage_account}.blob.core.windows.net/{container}/{rel}"
    now = datetime.now(timezone.utc)
    headers = {"Content-Type": "application/json", **storage_headers_common(now), "x-ms-blob-type": "BlockBlob"}
    headers["Authorization"] = shared_key_authorization(
        storage_account_name=storage_account,
        storage_account_key_b64=storage_key_b64,
        now_utc=now,
        method="PUT",
        url=url,
        headers=headers,
        content_length=len(content),
    )
    resp = request("PUT", url, headers=headers, body=content)
    if resp.status not in (200, 201):
        raise RuntimeError(f"Azure Blob returned HTTP {resp.status}")
 
