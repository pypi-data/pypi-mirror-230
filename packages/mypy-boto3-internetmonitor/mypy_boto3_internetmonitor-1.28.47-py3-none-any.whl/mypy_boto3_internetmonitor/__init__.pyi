"""
Main interface for internetmonitor service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_internetmonitor import (
        Client,
        CloudWatchInternetMonitorClient,
        ListHealthEventsPaginator,
        ListMonitorsPaginator,
    )

    session = Session()
    client: CloudWatchInternetMonitorClient = session.client("internetmonitor")

    list_health_events_paginator: ListHealthEventsPaginator = client.get_paginator("list_health_events")
    list_monitors_paginator: ListMonitorsPaginator = client.get_paginator("list_monitors")
    ```
"""
from .client import CloudWatchInternetMonitorClient
from .paginator import ListHealthEventsPaginator, ListMonitorsPaginator

Client = CloudWatchInternetMonitorClient

__all__ = (
    "Client",
    "CloudWatchInternetMonitorClient",
    "ListHealthEventsPaginator",
    "ListMonitorsPaginator",
)
