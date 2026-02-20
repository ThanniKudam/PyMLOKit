from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from pymlokit.constants import USER_AGENT


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


def _ssl_context(verify_ssl: bool) -> ssl.SSLContext | None:
    if verify_ssl:
        return None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def request(
    method: str,
    url: str,
    headers: Mapping[str, str] | None = None,
    body: bytes | None = None,
    timeout_s: float = 60.0,
    verify_ssl: bool = False,
) -> HttpResponse:
    h = dict(headers or {})
    h.setdefault("User-Agent", USER_AGENT)
    req = urllib.request.Request(url=url, data=body, method=method.upper(), headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=_ssl_context(verify_ssl)) as resp:
            return HttpResponse(
                status=int(resp.status),
                headers=dict(resp.headers.items()),
                body=resp.read(),
            )
    except urllib.error.HTTPError as e:
        return HttpResponse(status=int(e.code), headers=dict(e.headers.items()), body=e.read())


def get_json(
    url: str,
    headers: Mapping[str, str] | None = None,
    timeout_s: float = 60.0,
    verify_ssl: bool = False,
) -> tuple[int, Any]:
    resp = request(
        method="GET",
        url=url,
        headers={"Content-Type": "application/json", **(dict(headers or {}))},
        timeout_s=timeout_s,
        verify_ssl=verify_ssl,
    )
    if not resp.body:
        return resp.status, None
    return resp.status, json.loads(resp.body.decode("utf-8", errors="replace"))


def post_json(
    url: str,
    payload: Any,
    headers: Mapping[str, str] | None = None,
    timeout_s: float = 60.0,
    verify_ssl: bool = False,
) -> tuple[int, Any]:
    body = json.dumps(payload).encode("utf-8")
    resp = request(
        method="POST",
        url=url,
        headers={"Content-Type": "application/json", **(dict(headers or {}))},
        body=body,
        timeout_s=timeout_s,
        verify_ssl=verify_ssl,
    )
    if not resp.body:
        return resp.status, None
    return resp.status, json.loads(resp.body.decode("utf-8", errors="replace"))
