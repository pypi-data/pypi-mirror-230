"""Helper classes for scripts for cluster support packages."""

from cyberfusion.ClusterSupport._interfaces import (
    APIObjectInterface,
    sort_lists,
)

ENDPOINT_CUSTOMERS = "customers"
MODEL_CUSTOMERS = "customers"


class Customer(APIObjectInterface):
    """Represents object."""

    @sort_lists  # type: ignore[misc]
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.id = obj["id"]
        self.team_code = obj["team_code"]
        self.identifier = obj["identifier"]
        self.dns_subdomain = obj["dns_subdomain"]
        self.created_at = obj["created_at"]
        self.updated_at = obj["updated_at"]

    def create(self, *, team_code: str) -> None:
        """Create object."""
        url = f"/api/v1/{ENDPOINT_CUSTOMERS}"
        data = {"team_code": team_code}

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)

        self.support.customers.append(self)
