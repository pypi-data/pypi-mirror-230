"""Helper classes for scripts for cluster support packages."""

from cyberfusion.ClusterSupport._interfaces import (
    APIObjectInterface,
    sort_lists,
)

ENDPOINT_SERVICE_ACCOUNTS_TO_CLUSTERS = "service-accounts-to-clusters"


class ServiceAccountToCluster(APIObjectInterface):
    """Represents object."""

    @sort_lists  # type: ignore[misc]
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.id = obj["id"]
        self.service_account_id = obj["service_account_id"]
        self.cluster_id: int = obj["cluster_id"]
        self.created_at = obj["created_at"]
        self.updated_at = obj["updated_at"]

        self.service_account = self.support.get_service_accounts(
            id_=self.service_account_id
        )[0]
        self.cluster = self.support.get_clusters(id_=self.cluster_id)[0]

    def create(
        self,
        *,
        service_account_id: int,
        cluster_id: int,
    ) -> None:
        """Create object."""
        url = f"/api/v1/{ENDPOINT_SERVICE_ACCOUNTS_TO_CLUSTERS}"
        data = {
            "service_account_id": service_account_id,
            "cluster_id": cluster_id,
        }

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)

        self.support.service_accounts_to_clusters.append(self)

    def delete(self) -> None:
        """Delete object."""
        url = f"/api/v1/{ENDPOINT_SERVICE_ACCOUNTS_TO_CLUSTERS}/{self.id}"

        self.support.request.DELETE(url)
        self.support.request.execute()

        self.support.service_accounts_to_clusters.remove(self)
