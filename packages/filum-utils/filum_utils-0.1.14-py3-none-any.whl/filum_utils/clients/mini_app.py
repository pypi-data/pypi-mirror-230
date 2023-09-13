from typing import Dict, Any, List, TypedDict

from filum_utils.clients.common import BaseClient
from filum_utils.clients.log import LogClient, LogType
from filum_utils.config import config
from filum_utils.enums import ParentType


class InstalledMiniAppError(TypedDict):
    type: str
    message: str
    data: Any


class InstalledMiniAppsClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.APPSTORE_BASE_URL,
            username=config.APPSTORE_USERNAME,
            password=config.APPSTORE_PASSWORD
        )

    def get_list(self, mini_app_ids: List[int] = None, page: int = 0, size: int = 100):
        data = self._request(
            method="GET",
            endpoint="/internal/installed-mini-apps",
            params={
                "page": page,
                "size": size,
                "mini_app_ids": mini_app_ids
            }
        )

        return data.get("items") or []


class InstalledMiniAppClient(BaseClient):
    def __init__(self, installed_mini_app_id: int = None, installed_mini_app: Dict[str, Any] = None):
        super().__init__(
            base_url=config.APPSTORE_BASE_URL,
            username=config.APPSTORE_USERNAME,
            password=config.APPSTORE_PASSWORD
        )

        if installed_mini_app:
            self.installed_mini_app = installed_mini_app
        else:
            self.installed_mini_app = self._request(
                method="GET",
                endpoint=f"/internal/installed-mini-apps/{installed_mini_app_id}"
            )

        self.log_client = LogClient()

    def get_data(self, key: str):
        data = self.installed_mini_app.get("data")
        return data and data.get(key)

    def get_service_account_info(self):
        return self.installed_mini_app and self.installed_mini_app.get("service_account_info")

    def update_data(self, updated_data: Dict[str, Any]):
        self.installed_mini_app = self._request(
            method="PUT",
            endpoint=f"/internal/installed-mini-apps/{self.installed_mini_app['id']}/data",
            data=updated_data
        )

    def handle_update_failed(self, error: InstalledMiniAppError):
        self._log(
            type=LogType.ERROR,
            code="400",
            title="An error occurred when updating installed mini app",
            subtitle=error["message"],
            data=error["data"],
        )

    def _log(self, type: str, code: str, title: str, subtitle: str, data: str = None):
        self.log_client.create_log(
            parent_type=ParentType.INSTALLED_MINI_APP,
            parent_id=self.installed_mini_app["id"],
            type=type,
            code=code,
            title=title,
            subtitle=subtitle,
            data=data,
            member_organization_id=self.installed_mini_app.get("organization_id"),
        )
