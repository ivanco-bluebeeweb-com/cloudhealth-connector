"""Connection management for CloudHealth Connector: connect/disconnect/list.

Static Bearer API key -- verified synchronously against a harmless read
endpoint at connect time. No refresh logic needed (no expiry).
"""
from __future__ import annotations

import json
import uuid

from imperal_sdk import ActionResult

import cloudhealth_client as ch
from app import chat
from schemas import (
    NoParams,
    ConnectCloudHealthParams,
    ProviderConnection, ProviderConnectionList,
    DisconnectCloudHealthParams, DeleteResult,
)

_SECRET_NAME = "cloudhealth_connections"


async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET_NAME)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return data if isinstance(data, list) else []


async def _save_connections(ctx, connections: list[dict]) -> None:
    await ctx.secrets.set(_SECRET_NAME, json.dumps(connections))


async def resolve_connection(ctx, connection_id: str = "") -> dict | None:
    connections = await _load_connections(ctx)
    if not connections:
        return None
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                return c
        return None
    return connections[0]


async def resolve_or_error(ctx, connection_id: str = ""):
    conn = await resolve_connection(ctx, connection_id)
    if not conn:
        return None, ActionResult.error(
            "No CloudHealth connection found. Connect CloudHealth first.",
            code="CLOUDHEALTH_NOT_CONNECTED",
        )
    return conn, None


@chat.function(
    "connect_cloudhealth",
    "Connect your own CloudHealth (Broadcom/VMware) account by saving your API Key (from My Profile > Get API "
    "Key), after checking it actually works.",
    action_type="write", chain_callable=True, data_model=ProviderConnection,
    event="cloudhealth-connected", effects=["create:connection"],
)
async def connect_cloudhealth(ctx, params: ConnectCloudHealthParams) -> ActionResult:
    """Connect a CloudHealth account with a static API key."""
    if not params.api_key:
        return ActionResult.error("api_key is required.", code="CLOUDHEALTH_VALIDATION_FAILED")
    check = await ch.verify_key(params.api_key)
    if not check.get("ok"):
        return ActionResult.error(check.get("message", "Could not verify the CloudHealth API key."), code=check.get("code", "CLOUDHEALTH_UNAUTHORIZED"))
    connections = await _load_connections(ctx)
    conn_id = str(uuid.uuid4())
    entry = {"id": conn_id, "label": params.label or "CloudHealth account", "api_key": params.api_key}
    connections.append(entry)
    await _save_connections(ctx, connections)
    return ActionResult.success(ProviderConnection(id=conn_id, label=entry["label"]), summary="Cloudhealth connected.")


@chat.function(
    "list_connections",
    "List the connected CloudHealth accounts.",
    action_type="read", chain_callable=True, data_model=ProviderConnectionList,
)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """List connected CloudHealth accounts."""
    connections = await _load_connections(ctx)
    return ActionResult.success(ProviderConnectionList(
        connections=[ProviderConnection(id=c.get("id", ""), label=c.get("label", "")) for c in connections]
    ), summary="Connections listed.")


@chat.function(
    "disconnect_cloudhealth",
    "Disconnect a CloudHealth account: deletes the saved API Key. Nothing in CloudHealth itself is changed.",
    action_type="write", chain_callable=True, data_model=DeleteResult,
    event="cloudhealth-disconnected", effects=["delete:connection"],
)
async def disconnect_cloudhealth(ctx, params: DisconnectCloudHealthParams) -> ActionResult:
    """Disconnect a CloudHealth account."""
    connections = await _load_connections(ctx)
    remaining = [c for c in connections if c.get("id") != params.connection_id]
    if len(remaining) == len(connections):
        return ActionResult.error("No connection found with that id.", code="CLOUDHEALTH_NOT_FOUND")
    await _save_connections(ctx, remaining)
    return ActionResult.success(DeleteResult(deleted=True, id=params.connection_id), summary="Cloudhealth disconnected.")
