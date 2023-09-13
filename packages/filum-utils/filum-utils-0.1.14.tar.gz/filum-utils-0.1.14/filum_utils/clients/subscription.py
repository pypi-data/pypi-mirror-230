from typing import Dict, Any

from filum_utils.clients.common import BaseClient
from filum_utils.config import config
from filum_utils.enums import Organization
from filum_utils.types.subscription import Subscription


class SubscriptionClient(BaseClient):
    def __init__(self, subscription: Subscription, organization: Organization):
        super().__init__(
            base_url=config.SUBSCRIPTION_BASE_URL,
            username=config.SUBSCRIPTION_USERNAME,
            password=config.SUBSCRIPTION_PASSWORD
        )

        self.subscription = subscription
        self.organization = organization

    def update_data(self, updated_data: Dict[str, Any]):
        self._request(
            method="PUT",
            endpoint=f"/internal/subscriptions/{self.subscription['id']}",
            params={"organization_id": self.organization["id"]},
            data={"data": updated_data},
        )

    def publish(self, request_data: Dict[str, Any]):
        self._request(
            method="POST",
            endpoint=f"/internal/subscriptions/{self.subscription.get('id')}/publish",
            data={**request_data}
        )
