# CloudHealth Connector -- Preparation (v0.1)

## API surface
CloudHealth (Broadcom/VMware) Platform REST API (apidocs.cloudhealthtech.com)
-- resources: AWS/Azure/GCP accounts, assets, perspectives, billing/usage
reports (OLAP), metrics, policies, tagging. Confirmed via
apidocs.cloudhealthtech.com and github.com/CloudHealth/cht_api_guide
(2026-08-29).

## Auth model
Static per-user **API Key (GUID)** passed as a Bearer token --
`Authorization: Bearer YOUR_API_KEY` (confirmed via apidocs.cloudhealthtech.com
and apis.io/security/cloudhealth/cloudhealth-authentication; the API also
historically accepted an `api_key=` query param but that path was
deprecated in the 2019-04-25 product update in favor of the Authorization
header -- this connector uses the header only). Key is generated per-user
from Settings ("My Profile" -> "Get API Key"). No OAuth, no expiry --
same simplicity class as Vantage/Expensify/Brex.

## Why BYOK
Same reasoning as every other connector here -- the user's own
multi-cloud (AWS/Azure/GCP) cost, asset, and governance data is already
aggregated inside THEIR OWN CloudHealth account. The API key is
generated per CloudHealth user from their own account settings.

## Scope for v1
Read-heavy: cloud accounts, assets, perspectives (CloudHealth's custom
cost-allocation views), OLAP billing/usage reports, policies. Write:
none in v1 -- CloudHealth's write surface (creating/registering new
cloud provider accounts, custom policies) is an admin-level onboarding
operation best left to CloudHealth's own console for v1; deferred to v2.

## Rate limits / known constraints
Standard REST pagination. OLAP report queries require an explicit
report type/dimension/measure selection (CloudHealth's reporting DSL) --
exposed as raw query params rather than a full builder, matching how
Vantage's VQL and CloudZero's group_by params are handled in this
session's sibling connectors.
