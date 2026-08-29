"""Pydantic params/result models for CloudHealth Connector.

All params models are module-scope (V17 federal invariant, same rule as
every other connector this session's schemas.py).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class NoParams(BaseModel):
    """Explicit empty params model -- V17 disallows untyped handlers."""
    pass


class ConnectionScoped(BaseModel):
    connection_id: str = Field(
        "",
        description="Which connected CloudHealth account to use (see list_connections). Omit if only one is connected.",
    )


# ──────────────────────────────────────────────────────────────────────────
# Connection -- static Bearer API key, no OAuth
# ──────────────────────────────────────────────────────────────────────────


class ConnectCloudHealthParams(BaseModel):
    api_key: str = Field("", description="Your CloudHealth API Key (from My Profile > Get API Key).")
    label: str = Field("", description="Optional friendly label for this connection, e.g. 'Acme Inc CloudHealth'.")


class ProviderConnection(BaseModel):
    id: str = ""
    label: str = ""


class ProviderConnectionList(BaseModel):
    connections: list[ProviderConnection] = Field(default_factory=list)


class DisconnectCloudHealthParams(BaseModel):
    connection_id: str = Field(description="Which connection to disconnect (see list_connections).")


class DeleteResult(BaseModel):
    deleted: bool = False
    id: str = ""


# ──────────────────────────────────────────────────────────────────────────
# Reads
# ──────────────────────────────────────────────────────────────────────────


class ListAccountsParams(ConnectionScoped):
    limit: int = Field(50, ge=1, le=200, description="Maximum accounts to return.")


class AccountList(BaseModel):
    count: int = 0
    accounts: list[dict] = Field(default_factory=list)


class GetAccountParams(ConnectionScoped):
    account_id: str = Field(description="The CloudHealth account id.")


class AccountDetail(BaseModel):
    account: dict = Field(default_factory=dict)


class ListAssetsParams(ConnectionScoped):
    asset_type: str = Field(description="Asset type, e.g. 'AwsInstance', 'AwsS3Bucket', 'AzureVirtualMachine'.")
    limit: int = Field(50, ge=1, le=200, description="Maximum assets to return.")


class AssetList(BaseModel):
    asset_type: str = ""
    count: int = 0
    assets: list[dict] = Field(default_factory=list)


class ListPerspectivesParams(ConnectionScoped):
    pass


class PerspectiveList(BaseModel):
    count: int = 0
    perspectives: list[dict] = Field(default_factory=list)


class GetPerspectiveParams(ConnectionScoped):
    perspective_id: str = Field(description="The CloudHealth perspective id.")


class PerspectiveDetail(BaseModel):
    perspective: dict = Field(default_factory=dict)


class ListPoliciesParams(ConnectionScoped):
    limit: int = Field(50, ge=1, le=200, description="Maximum policies to return.")


class PolicyList(BaseModel):
    count: int = 0
    policies: list[dict] = Field(default_factory=list)


class RunOlapReportParams(ConnectionScoped):
    report_type: str = Field(description="OLAP report name, e.g. 'AwsBillingInvoice', 'AwsMonthlyBillingUsage'.")
    dimensions: str = Field("", description="Optional comma-separated dimension names, e.g. 'Account,Service'.")
    measures: str = Field("cost", description="Optional comma-separated measure names, e.g. 'cost,usage'.")
    interval: str = Field("last_month", description="Time interval, e.g. 'last_month', 'last_7_days'.")


class OlapReportResult(BaseModel):
    report_type: str = ""
    rows: list[dict] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────
# Value-add reports
# ──────────────────────────────────────────────────────────────────────────


class GetSpendOverviewParams(ConnectionScoped):
    interval: str = Field("last_month", description="Time interval, e.g. 'last_month', 'last_7_days'.")


class SpendOverviewReport(BaseModel):
    interval: str = ""
    total_spend: float = 0.0
    by_service: dict[str, float] = Field(default_factory=dict)
