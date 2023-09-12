from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List

from filum_utils.clients.action import ActionError
from filum_utils.clients.filum import FilumClient
from filum_utils.clients.log import LogClient, LogType
from filum_utils.clients.notification import (
    NotificationClient,
    NOTIFICATION_ERROR_MESSAGE_MAPPINGS,
)
from filum_utils.clients.subscription import SubscriptionClient
from filum_utils.types.organization import Organization
from filum_utils.types.subscription import Subscription, SubscriptionData

Event = Optional[Dict[str, Any]]
User = Optional[Dict[str, Any]]
Object = Optional[Dict[str, Any]]


class SubscriptionService(ABC):
    def __init__(self, subscription: Subscription, organization: Organization):
        self.subscription_client = SubscriptionClient(subscription, organization)
        self.filum_client = FilumClient()
        self.log_client = LogClient()
        self.notification_client = NotificationClient()

        self.subscription = subscription
        self.organization = organization

    @property
    def subscription_data(self) -> SubscriptionData:
        return self.subscription.get("data")

    @property
    @abstractmethod
    def parent(self):
        ...

    @property
    @abstractmethod
    def member_account_id(self):
        ...

    @property
    @abstractmethod
    def run_type(self):
        ...

    @property
    @abstractmethod
    def _parent_type(self):
        ...

    @property
    @abstractmethod
    def _notification_route(self):
        ...

    @property
    @abstractmethod
    def _notification_publisher_type(self):
        ...

    def update_subscription_data(self, updated_data: Dict[str, Any]):
        self.subscription_client.update_data(updated_data)

    def handle_trigger_failed(self, error: ActionError, notify: bool):
        self._log(
            parent_type=f"{self._parent_type}",
            type=LogType.ERROR,
            code="400",
            title="An error occurred when triggering your action, please contact Filum for support.",
            subtitle=error["message"],
            data=error["data"],
        )

        if notify:
            self._notify(
                publisher_type=f"{self._notification_publisher_type}",
                title=f"{self.parent.get('name')} failed to run",
                subtitle=error.get("notification_message") or NOTIFICATION_ERROR_MESSAGE_MAPPINGS[error["type"]],
            )

    @abstractmethod
    def handle_real_time_trigger(self, process_real_time_fn: Callable, event: [Dict[str, Any]], **kwargs):
        ...

    @abstractmethod
    def handle_segment_manual_trigger(
        self,
        process_segment_manual_fn: Callable,
        properties: List[str],
        required_properties: Optional[List[List[str]]] = None,
        last_current_index: int = 0,
        **kwargs,
    ):
        ...

    @abstractmethod
    def handle_file_manual_trigger(
        self,
        process_file_manual_fn: Callable,
        file_name: str,
        last_current_row: int = 0,
        **kwargs,
    ):
        ...

    @abstractmethod
    def handle_object_manual_trigger(
        self,
        process_object_manual_fn: Callable,
        **kwargs,
    ):
        ...

    def _log(self, parent_type: str, type: str, code: str, title: str, subtitle: str, data: str = None):
        self.log_client.create_log(
            parent_type=parent_type,
            parent_id=self.parent["id"],
            type=type,
            code=code,
            title=title,
            subtitle=subtitle,
            data=data,
            member_account_id=self.member_account_id,
            member_organization_id=self.organization.get("id"),
        )

    def _notify(self, publisher_type: str, title: str, subtitle: str):
        self.notification_client.create_notification(
            publisher_type=publisher_type,
            title=title,
            subtitle=subtitle,
            route=self._notification_route,
            member_account_id=self.member_account_id,
            member_organization_id=self.organization.get("id"),
        )
