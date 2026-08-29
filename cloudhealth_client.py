"""Thin HTTP client for CloudHealth (Broadcom/VMware) Platform API.

Static Bearer API key -- no OAuth. Same "fail()-dict + ClientFail
exception" shape as every other connector this session's *_client.py.
"""
from __future__ import annotations

from typing import Any

import httpx

API_BASE = "https://chapi.cloudhealthtech.com"

CLOUDHEALTH_NOT_CONNECTED = "CLOUDHEALTH_NOT_CONNECTED"
CLOUDHEALTH_UNAUTHORIZED = "CLOUDHEALTH_UNAUTHORIZED"
CLOUDHEALTH_FORBIDDEN = "CLOUDHEALTH_FORBIDDEN"
CLOUDHEALTH_NOT_FOUND = "CLOUDHEALTH_NOT_FOUND"
CLOUDHEALTH_RATE_LIMITED = "CLOUDHEALTH_RATE_LIMITED"
CLOUDHEALTH_BACKEND_ERROR = "CLOUDHEALTH_BACKEND_ERROR"
CLOUDHEALTH_VALIDATION_FAILED = "CLOUDHEALTH_VALIDATION_FAILED"

_MESSAGES = {
    CLOUDHEALTH_NOT_CONNECTED: "No CloudHealth connection found. Connect CloudHealth first.",
    CLOUDHEALTH_UNAUTHORIZED: "CloudHealth rejected the API key as invalid.",
    CLOUDHEALTH_FORBIDDEN: "CloudHealth rejected this request -- the connected account lacks permission for this resource.",
    CLOUDHEALTH_NOT_FOUND: "That CloudHealth record was not found.",
    CLOUDHEALTH_RATE_LIMITED: "CloudHealth rate-limited this request. Try again shortly.",
    CLOUDHEALTH_BACKEND_ERROR: "CloudHealth's API returned an error.",
    CLOUDHEALTH_VALIDATION_FAILED: "CloudHealth rejected the request as invalid.",
}


class ClientFail(Exception):
    def __init__(self, payload: dict):
        self.payload = payload
        super().__init__(payload.get("message", "CloudHealth request failed"))


def fail(code: str, detail: str = "") -> dict:
    msg = _MESSAGES.get(code, "CloudHealth request failed.")
    if detail:
        msg = f"{msg} ({detail})"
    return {"ok": False, "code": code, "message": msg}


async def verify_key(api_key: str) -> dict:
    """Verify an API key works by calling a harmless read endpoint."""
    if not api_key:
        return fail(CLOUDHEALTH_VALIDATION_FAILED, "api_key is required")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(f"{API_BASE}/v1/aws_accounts", headers=headers, params={"per_page": 1})
        except httpx.RequestError as e:
            return fail(CLOUDHEALTH_BACKEND_ERROR, str(e))
    if resp.status_code == 401:
        return fail(CLOUDHEALTH_UNAUTHORIZED)
    if resp.status_code == 403:
        return fail(CLOUDHEALTH_FORBIDDEN)
    if resp.status_code >= 400:
        return fail(CLOUDHEALTH_BACKEND_ERROR, f"HTTP {resp.status_code}")
    return {"ok": True}


def _check_status(resp: httpx.Response, action: str) -> Any:
    if resp.status_code == 401:
        raise ClientFail(fail(CLOUDHEALTH_UNAUTHORIZED))
    if resp.status_code == 403:
        raise ClientFail(fail(CLOUDHEALTH_FORBIDDEN, action))
    if resp.status_code == 404:
        raise ClientFail(fail(CLOUDHEALTH_NOT_FOUND, action))
    if resp.status_code == 429:
        raise ClientFail(fail(CLOUDHEALTH_RATE_LIMITED))
    if resp.status_code >= 400:
        raise ClientFail(fail(CLOUDHEALTH_BACKEND_ERROR, f"HTTP {resp.status_code} on {action}"))
    if not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        return {}


async def request(ctx, conn: dict, method: str, path: str, *, params: dict | None = None,
                   json_body: dict | None = None, action: str = "") -> Any:
    api_key = conn.get("api_key", "")
    if not api_key:
        raise ClientFail(fail(CLOUDHEALTH_NOT_CONNECTED))
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.request(method, f"{API_BASE}{path}", headers=headers, params=params, json=json_body)
        except httpx.RequestError as e:
            raise ClientFail(fail(CLOUDHEALTH_BACKEND_ERROR, str(e)))
    return _check_status(resp, action or path)
