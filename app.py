"""Extension declaration, secrets, lifecycle hooks.

WHY BYOK, same reasoning as every other connector here -- the user's own
multi-cloud (AWS/Azure/GCP) cost, asset, and governance data is already
aggregated inside THEIR OWN CloudHealth (Broadcom/VMware) account.

WHY A STATIC BEARER API KEY (confirmed against apidocs.cloudhealthtech.com
and apis.io/security/cloudhealth/cloudhealth-authentication, 2026-08-29):
CloudHealth issues a per-user API Key (GUID) from account Settings, sent
as "Authorization: Bearer <key>". The legacy api_key= query-param method
was deprecated in 2019 in favor of the header -- this connector uses the
header only.

WHY NO WRITES IN V1: CloudHealth's write surface (registering new cloud
provider accounts, creating governance policies) is an admin-level
onboarding operation best done in CloudHealth's own console -- deferred
to v2 per PREPARATION.md rather than shoehorned into this read-focused v1.
"""
from __future__ import annotations

from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "cloudhealth-connector",
    version="0.1.0",
    display_name="CloudHealth",
    icon="icon.svg",
    capabilities=["cloudhealth:read"],
    description=(
        "Connect your own CloudHealth (Broadcom/VMware) account (bring your own API Key from your account "
        "settings) to read cloud provider accounts, assets, perspectives (cost-allocation views), OLAP "
        "billing/usage reports, and governance policies, plus a value-add spend overview report. Read-only "
        "in this release -- registering new cloud accounts and creating policies remain in the CloudHealth "
        "console for now."
    ),
)

chat = ChatExtension(ext)
