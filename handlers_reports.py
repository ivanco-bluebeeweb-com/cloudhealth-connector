"""Value-add report for CloudHealth Connector -- spend overview by
service, using CloudHealth's own AwsMonthlyBillingUsage OLAP report,
same "aggregate raw records into one glance" shape as every other
connector's handlers_reports.py this session.
"""
from __future__ import annotations

from imperal_sdk import ActionResult

import cloudhealth_client as ch
from app import chat
from handlers_connection import resolve_or_error
from schemas import GetSpendOverviewParams, SpendOverviewReport


@chat.function(
    "get_spend_overview_report",
    "Value-add report: summarize recent CloudHealth billing usage by cloud service for a chosen time interval.",
    action_type="read", chain_callable=True, data_model=SpendOverviewReport,
)
async def get_spend_overview_report(ctx, params: GetSpendOverviewParams) -> ActionResult:
    """Scan an AWS monthly billing usage OLAP report grouped by service."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if not conn:
        return err
    query = {"interval": params.interval, "dimensions[]": ["Service"], "measures[]": ["cost"]}
    data = await ch.request(ctx, conn, "GET", "/olap_reports/AwsMonthlyBillingUsage", params=query, action="get billing usage for spend overview")
    rows = data.get("data", data) if isinstance(data, dict) else data
    rows = rows if isinstance(rows, list) else []
    total = 0.0
    by_service: dict[str, float] = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        service = r.get("Service") or r.get("service") or "Unknown"
        try:
            cost = float(r.get("cost", 0) or 0)
        except (TypeError, ValueError):
            continue
        total += cost
        by_service[service] = by_service.get(service, 0.0) + cost
    return ActionResult.ok(SpendOverviewReport(
        interval=params.interval,
        total_spend=round(total, 2),
        by_service={k: round(v, 2) for k, v in by_service.items()},
    ))
