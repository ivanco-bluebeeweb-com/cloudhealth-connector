"""Read-only entity layer for CloudHealth Connector.

No generic writes in v1 -- CloudHealth's write surface (registering new
cloud accounts, creating policies) stays in the CloudHealth console for
this release, per PREPARATION.md/app.py.
"""
from __future__ import annotations

from imperal_sdk import ActionResult

import cloudhealth_client as ch
from app import chat
from handlers_connection import resolve_or_error
from schemas import (
    ListAccountsParams, AccountList,
    GetAccountParams, AccountDetail,
    ListAssetsParams, AssetList,
    ListPerspectivesParams, PerspectiveList,
    GetPerspectiveParams, PerspectiveDetail,
    ListPoliciesParams, PolicyList,
    RunOlapReportParams, OlapReportResult,
)


@chat.function(
    "list_accounts",
    "List cloud provider accounts (AWS/Azure/GCP) registered in the connected CloudHealth account.",
    action_type="read", chain_callable=True, data_model=AccountList,
)
async def list_accounts(ctx, params: ListAccountsParams) -> ActionResult:
    """List cloud provider accounts."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ch.request(ctx, conn, "GET", "/v1/aws_accounts", params={"per_page": params.limit}, action="list accounts")
    rows = data.get("aws_accounts", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(AccountList(count=len(rows), accounts=rows))


@chat.function(
    "get_account",
    "Read one cloud provider account in full by its CloudHealth account id.",
    action_type="read", chain_callable=True, data_model=AccountDetail,
)
async def get_account(ctx, params: GetAccountParams) -> ActionResult:
    """Read one account."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ch.request(ctx, conn, "GET", f"/v1/aws_accounts/{params.account_id}", action="get account")
    return ActionResult.ok(AccountDetail(account=data if isinstance(data, dict) else {}))


@chat.function(
    "list_assets",
    "List assets of a given type (e.g. AwsInstance, AwsS3Bucket, AzureVirtualMachine) tracked in CloudHealth.",
    action_type="read", chain_callable=True, data_model=AssetList,
)
async def list_assets(ctx, params: ListAssetsParams) -> ActionResult:
    """List assets of a given type."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ch.request(ctx, conn, "GET", f"/v1/{params.asset_type}", params={"per_page": params.limit}, action=f"list {params.asset_type} assets")
    rows = data if isinstance(data, list) else data.get(params.asset_type, []) if isinstance(data, dict) else []
    return ActionResult.ok(AssetList(asset_type=params.asset_type, count=len(rows), assets=rows))


@chat.function(
    "list_perspectives",
    "List perspectives (CloudHealth's custom cost-allocation views) configured on the connected account.",
    action_type="read", chain_callable=True, data_model=PerspectiveList,
)
async def list_perspectives(ctx, params: ListPerspectivesParams) -> ActionResult:
    """List perspectives."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ch.request(ctx, conn, "GET", "/v1/perspective_schemas", action="list perspectives")
    rows = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
    return ActionResult.ok(PerspectiveList(count=len(rows), perspectives=rows))


@chat.function(
    "get_perspective",
    "Read one perspective's schema in full by its CloudHealth perspective id.",
    action_type="read", chain_callable=True, data_model=PerspectiveDetail,
)
async def get_perspective(ctx, params: GetPerspectiveParams) -> ActionResult:
    """Read one perspective."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ch.request(ctx, conn, "GET", f"/v1/perspective_schemas/{params.perspective_id}", action="get perspective")
    return ActionResult.ok(PerspectiveDetail(perspective=data if isinstance(data, dict) else {}))


@chat.function(
    "list_policies",
    "List governance policies configured on the connected CloudHealth account.",
    action_type="read", chain_callable=True, data_model=PolicyList,
)
async def list_policies(ctx, params: ListPoliciesParams) -> ActionResult:
    """List policies."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    data = await ch.request(ctx, conn, "GET", "/v1/policies", params={"per_page": params.limit}, action="list policies")
    rows = data if isinstance(data, list) else data.get("policies", []) if isinstance(data, dict) else []
    return ActionResult.ok(PolicyList(count=len(rows), policies=rows))


@chat.function(
    "run_olap_report",
    "Run a CloudHealth OLAP billing/usage report (e.g. AwsBillingInvoice, AwsMonthlyBillingUsage) with chosen "
    "dimensions, measures, and a time interval.",
    action_type="read", chain_callable=True, data_model=OlapReportResult,
)
async def run_olap_report(ctx, params: RunOlapReportParams) -> ActionResult:
    """Run an OLAP report."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    query: dict = {"interval": params.interval, "measures[]": params.measures.split(",")}
    if params.dimensions:
        query["dimensions[]"] = params.dimensions.split(",")
    data = await ch.request(ctx, conn, "GET", f"/olap_reports/{params.report_type}", params=query, action=f"run {params.report_type} report")
    rows = data.get("data", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    return ActionResult.ok(OlapReportResult(report_type=params.report_type, rows=rows))
