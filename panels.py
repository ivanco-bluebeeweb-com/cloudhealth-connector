"""Panel UI -- connections list/connect form + the one required "App
settings" entry point, same shape as every other connector this
session's panels.py.

SIDEBAR CONTENT -- NO CARDS ANYWHERE, per ~/UI_INTERFACE_STANDARD.md's
"left sidebar, no decorated cards" rule. Disconnect lives only in the
"App settings" screen (panels_settings.py). The one secondary "App
settings" button is always the LAST element at the bottom of the sidebar.

PER ~/UI_INTERFACE_STANDARD.md (2026-08-21 addendum): every Input carries
its own visible label (a ui.Text wrapping the ui.Input in a Stack -- ui.Input
itself does not accept label=), the placeholder text is always contextually
specific. The "How do I set this up?" instructions live ONLY in the help
overlay below -- never duplicated as static sidebar text.

KNOWN UI COMPONENT PITFALLS (learned building Ramp/Brex/Vantage/CloudZero
Connectors, 2026-08-29): ui.Stack does NOT accept (only
ui.Button does). ui.Input does NOT accept secret=True -- use
ui.Password(param_name=..., placeholder=...) instead. ui.Form does NOT
accept on_submit= -- use action="tool_name" (a plain string) instead.
"""
from __future__ import annotations

from imperal_sdk import ui

from app import ext
import handlers_connection as h


def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings", variant="secondary", size="sm", icon="settings", on_click=ui.Call("__panel__cloudhealth_settings"),
    )


def _connection_row(c: dict) -> ui.UINode:
    label = c.get("label") or "CloudHealth connection"
    return ui.Stack(direction="v", gap=1, children=[
        ui.Text(label, variant="body"),
        ui.Text("Connected", variant="caption"),
    ])


def _connections_section(connections: list[dict]) -> ui.UINode:
    if not connections:
        return ui.Text("No CloudHealth accounts connected yet.", variant="caption")
    children: list[ui.UINode] = []
    for i, c in enumerate(connections):
        if i > 0:
            children.append(ui.Divider())
        children.append(_connection_row(c))
    return ui.Stack(direction="v", gap=2, children=children)


def _connect_section() -> ui.UINode:
    return ui.Stack(direction="v", gap=2, children=[
        ui.Text("Connect a CloudHealth account", variant="heading"),
        ui.Form(
            action="connect_cloudhealth",
            submit_label="Connect CloudHealth",
            children=[
                ui.Stack(direction="v", gap=1, children=[
                    ui.Text("Friendly label (optional)", variant="label"),
                    ui.Input(param_name="label", placeholder="e.g. Acme Inc CloudHealth"),
                ]),
                ui.Stack(direction="v", gap=1, children=[
                    ui.Text("API Key", variant="label"),
                    ui.Password(param_name="api_key", placeholder="API Key from My Profile > Get API Key"),
                ]),
            ],
        ),
        ui.Button(
            "How do I set this up?", variant="ghost", size="sm", on_click=ui.Call("__panel__cloudhealth_connect_help"),
        ),
    ])


@ext.panel("cloudhealth_connect", slot="left", title="CloudHealth")
async def cloudhealth_connect(ctx, **kwargs) -> object:
    connections = await h._load_connections(ctx)
    children: list[ui.UINode] = []
    if connections:
        children.append(_connections_section(connections))
        children.append(ui.Divider())
    children.append(_connect_section())
    children.append(ui.Divider())
    children.append(_settings_button())
    return ui.Stack(direction="v", gap=3, children=children)


@ext.panel("cloudhealth_connect_help", slot="overlay", title="How do I set this up?")
async def cloudhealth_connect_help(ctx, **kwargs) -> object:
    return ui.Stack(direction="v", gap=2, children=[
        ui.Text(
            "1. Log into your CloudHealth (Broadcom/VMware) account.\n"
            "2. Open your profile menu (top right) and choose 'My Profile'.\n"
            "3. Click 'Get API Key' to reveal your personal API Key.\n"
            "4. Paste that key here to connect. It never expires and has no OAuth to manage.",
            variant="body",
        ),
    ])
