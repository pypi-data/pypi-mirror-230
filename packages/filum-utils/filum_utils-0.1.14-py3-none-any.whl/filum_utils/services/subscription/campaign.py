from typing import Dict, Any, Optional, Callable, List

from filum_utils.clients.notification import RoutePath, PublisherType
from filum_utils.config import config
from filum_utils.enums import ParentType
from filum_utils.errors import BaseError
from filum_utils.services.file import FileService
from filum_utils.services.subscription import SubscriptionService
from filum_utils.types.action import Action
from filum_utils.types.campaign import Campaign
from filum_utils.types.common import CallableResponse, TriggerFunctionResponse
from filum_utils.types.organization import Organization
from filum_utils.types.subscription import Subscription, SubscriptionData

Event = Optional[Dict[str, Any]]
User = Optional[Dict[str, Any]]


class CampaignSubscriptionService(SubscriptionService):
    def __init__(self, campaign: Campaign, subscription: Subscription, action: Action, organization: Organization):
        super().__init__(subscription, organization)

        self.campaign = campaign
        self.action = action

    @property
    def parent(self):
        return self.campaign

    @property
    def member_account_id(self):
        account = self.campaign["account"] or {}
        return account.get("id")

    @property
    def run_type(self):
        return self.campaign.get("run_type")

    @property
    def _parent_type(self):
        return ParentType.CAMPAIGN

    @property
    def _notification_route(self):
        return {
            "path": RoutePath.CAMPAIGNS_DETAIL,
            "params": {
                "solutionGroup": "cx",
                "solutionId": "dynamic_feedback",
                "campaignId": self.campaign["id"]
            }
        }

    @property
    def _notification_publisher_type(self):
        return PublisherType.FEEDBACK_360

    def handle_real_time_trigger(
        self,
        process_real_time_fn: Callable[
            [Action, Campaign, Organization, Event, SubscriptionData, Any],
            CallableResponse
        ],
        event: [Dict[str, Any]],
        **kwargs
    ) -> TriggerFunctionResponse:
        result = self._handle_trigger(
            process_real_time_fn,
            event,
            **kwargs
        )

        return {
            "is_finished": True,
            "success_count": result.get("success_count")
        }

    def handle_segment_manual_trigger(
        self,
        process_segment_manual_fn: Callable[
            [Action, Campaign, Organization, List[User], SubscriptionData, Any],
            CallableResponse
        ],
        properties: List[str],
        required_properties: Optional[List[List[str]]] = None,
        last_current_index: int = 0,
        **kwargs,
    ):
        current_index = self.subscription_data.get("last_current_index") or 0
        if current_index != last_current_index:
            raise BaseError(
                message="Last current index not matched",
                data={
                    "Campaign ID": self.campaign["id"],
                    "Current Index": current_index,
                    "Last Current Index": last_current_index
                }
            )

        users = self.filum_client.get_user_csv_reader(
            properties=properties,
            object_ids=[self.campaign.get("segment_id")],
            object_type="segment",
            organization=self.organization,
            required_properties=required_properties,
            offset=current_index,
            limit=config.SEGMENT_RECORD_LIMIT
        )

        total_users = len(users) if users else 0
        current_index = total_users + current_index

        result = self._handle_trigger(
            process_fn=process_segment_manual_fn,
            data=users,
            **kwargs,
        )

        if total_users >= config.SEGMENT_RECORD_LIMIT:
            self.update_subscription_data({"last_current_index": current_index})
            self.subscription_client.publish(
                self.subscription["id"],
                {"last_current_index": current_index}
            )

            return {
                "is_finished": False,
                "success_count": result.get("success_count")
            }

        return {
            "is_finished": True,
            "success_count": result.get("success_count")
        }

    def handle_file_manual_trigger(
        self,
        process_file_manual_fn: Callable,
        last_current_index: int = 0,
        **kwargs,
    ):
        current_index = self.subscription_data.get("last_current_index") or 0
        if current_index != last_current_index:
            raise BaseError(
                message="Last current index not matched",
                data={
                    "Campaign ID": self.campaign["id"],
                    "Current Index": current_index,
                    "Last Current Index": last_current_index
                }
            )

        trigger_data = self.subscription_data.get("trigger_data")
        file_name = trigger_data.get("file_name")
        if not file_name:
            raise BaseError(
                message="Missing file",
                data={
                    "Campaign ID": self.campaign["id"],
                }
            )

        file_content_bytes = self.filum_client.get_uploaded_file(file_name)
        users = FileService.get_rows(
            file_name,
            file_content_bytes,
            current_index=current_index
        )

        result = self._handle_trigger(
            process_fn=process_file_manual_fn,
            data=users,
            **kwargs,
        )

        total_users = len(users) if users else 0
        current_index = total_users + current_index
        if total_users >= config.FILE_RECORD_LIMIT:
            self.update_subscription_data({"last_current_index": current_index})
            self.subscription_client.publish(
                self.subscription["id"],
                {"last_current_index": current_index}
            )

            return {
                "is_finished": False,
                "success_count": result.get("success_count")
            }

        return {
            "is_finished": True,
            "success_count": result.get("success_count")
        }

    def handle_object_manual_trigger(
        self,
        process_object_manual_fn: Callable,
        **kwargs,
    ):
        ...

    def _handle_trigger(
        self,
        process_fn: Callable,
        data: Any,
        **kwargs,
    ):
        params = {
            "action": self.action,
            "campaign": self.campaign,
            "data": data,
            "subscription_data": self.subscription_data,
            "organization": self.organization,
            **kwargs
        }

        return process_fn(**params)
