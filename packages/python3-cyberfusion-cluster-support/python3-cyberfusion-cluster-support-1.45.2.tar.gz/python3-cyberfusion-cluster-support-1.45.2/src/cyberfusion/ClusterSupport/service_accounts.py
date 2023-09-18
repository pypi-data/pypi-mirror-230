"""Helper classes for scripts for cluster support packages."""

import enum

from cyberfusion.ClusterSupport._interfaces import (
    APIObjectInterface,
    sort_lists,
)

ENDPOINT_SERVICE_ACCOUNTS = "service-accounts"


class ServiceAccountGroup(str, enum.Enum):
    """Service account groups."""

    SECURITY_TXT_POLICY_SERVER: str = "Security TXT Policy Server"
    LOAD_BALANCER: str = "Load Balancer"
    MAIL_PROXY: str = "Mail Proxy"
    MAIL_GATEWAY: str = "Mail Gateway"


class ServiceAccount(APIObjectInterface):
    """Represents object."""

    @sort_lists  # type: ignore[misc]
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.id = obj["id"]
        self.name = obj["name"]
        self.group = obj["group"]
        self.created_at = obj["created_at"]
        self.updated_at = obj["updated_at"]

    def create(self, *, name: str, group: ServiceAccountGroup) -> None:
        """Create object."""
        url = f"/api/v1/{ENDPOINT_SERVICE_ACCOUNTS}"
        data = {"name": name, "group": group}

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)

        self.support.service_accounts.append(self)

    def delete(self) -> None:
        """Delete object."""
        url = f"/api/v1/{ENDPOINT_SERVICE_ACCOUNTS}/{self.id}"

        self.support.request.DELETE(url)
        self.support.request.execute()

        self.support.service_accounts.remove(self)
