"""
Type annotations for internetmonitor service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_internetmonitor/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_internetmonitor.client import CloudWatchInternetMonitorClient
    from mypy_boto3_internetmonitor.paginator import (
        ListHealthEventsPaginator,
        ListMonitorsPaginator,
    )

    session = Session()
    client: CloudWatchInternetMonitorClient = session.client("internetmonitor")

    list_health_events_paginator: ListHealthEventsPaginator = client.get_paginator("list_health_events")
    list_monitors_paginator: ListMonitorsPaginator = client.get_paginator("list_monitors")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator, Paginator

from .literals import HealthEventStatusType
from .type_defs import (
    ListHealthEventsOutputTypeDef,
    ListMonitorsOutputTypeDef,
    PaginatorConfigTypeDef,
    TimestampTypeDef,
)

__all__ = ("ListHealthEventsPaginator", "ListMonitorsPaginator")


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListHealthEventsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/internetmonitor.html#CloudWatchInternetMonitor.Paginator.ListHealthEvents)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_internetmonitor/paginators/#listhealtheventspaginator)
    """

    def paginate(
        self,
        *,
        MonitorName: str,
        StartTime: TimestampTypeDef = ...,
        EndTime: TimestampTypeDef = ...,
        EventStatus: HealthEventStatusType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListHealthEventsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/internetmonitor.html#CloudWatchInternetMonitor.Paginator.ListHealthEvents.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_internetmonitor/paginators/#listhealtheventspaginator)
        """


class ListMonitorsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/internetmonitor.html#CloudWatchInternetMonitor.Paginator.ListMonitors)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_internetmonitor/paginators/#listmonitorspaginator)
    """

    def paginate(
        self, *, MonitorStatus: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListMonitorsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/internetmonitor.html#CloudWatchInternetMonitor.Paginator.ListMonitors.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_internetmonitor/paginators/#listmonitorspaginator)
        """
