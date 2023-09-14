import os

from prometheus_client import CollectorRegistry, Counter, Gauge, start_http_server

# Create a custom CollectorRegistry
registry_package = CollectorRegistry()
export_lag = Gauge(
    "export_lag",
    "The average time from when the data changes in GDN collections are reflected in external data sources",
    ["region", "tenant", "fabric", "workflow"],
    registry=registry_package,
)
export_errors = Counter(
    "export_errors",
    "Total count of errors while exporting data from GDN collections",
    ["region", "tenant", "fabric", "workflow"],
    registry=registry_package,
)

region_label = os.getenv("GDN_FEDERATION", "NA")
tenant_label = os.getenv("GDN_TENANT", "NA")
fabric_label = os.getenv("GDN_FABRIC", "NA")
workflow_label = os.getenv("WORKFLOW_UUID", "NA")
