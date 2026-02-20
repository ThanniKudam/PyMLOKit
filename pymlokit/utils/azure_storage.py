from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime
from typing import Mapping
from urllib.parse import parse_qsl, urlparse


def _rfc1123(dt: datetime) -> str:
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def canonicalized_headers(headers: Mapping[str, str]) -> str:
    items = []
    for k, v in headers.items():
        if k.lower().startswith("x-ms-"):
            items.append((k.lower(), " ".join(v.split())))
    items.sort(key=lambda kv: kv[0])
    return "".join(f"{k}:{v}\n" for k, v in items)


def canonicalized_resource(url: str, storage_account_name: str) -> str:
    parsed = urlparse(url)
    sb = f"/{storage_account_name}{parsed.path}"
    params = parse_qsl(parsed.query, keep_blank_values=True)
    grouped: dict[str, list[str]] = {}
    for k, v in params:
        grouped.setdefault(k, []).append(v)
    for k in sorted(grouped.keys()):
        sb += f"\n{k}:{','.join(grouped[k])}"
    return sb


def shared_key_authorization(
    *,
    storage_account_name: str,
    storage_account_key_b64: str,
    now_utc: datetime,
    method: str,
    url: str,
    headers: Mapping[str, str],
    content_length: int | None,
    if_match: str = "",
    content_md5: str = "",
) -> str:
    cl = "" if method.upper() in ("GET", "HEAD") else str(int(content_length or 0))
    message_signature = (
        f"{method.upper()}\n\n\n{cl}\n{content_md5}\n\n\n\n{if_match}\n\n\n\n"
        f"{canonicalized_headers(headers)}{canonicalized_resource(url, storage_account_name)}"
    )
    key = base64.b64decode(storage_account_key_b64)
    sig = base64.b64encode(hmac.new(key, message_signature.encode("utf-8"), hashlib.sha256).digest()).decode("utf-8")
    return f"SharedKey {storage_account_name}:{sig}"


def storage_headers_common(now_utc: datetime) -> dict[str, str]:
    return {
        "x-ms-date": _rfc1123(now_utc),
        "x-ms-version": "2021-08-06",
    }
