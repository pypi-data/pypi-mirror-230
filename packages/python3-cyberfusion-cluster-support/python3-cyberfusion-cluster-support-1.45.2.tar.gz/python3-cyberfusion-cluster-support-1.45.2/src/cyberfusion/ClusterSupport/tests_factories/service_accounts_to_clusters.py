"""Factories for API object."""

import factory

from cyberfusion.ClusterSupport.service_accounts_to_clusters import (
    ServiceAccountToCluster,
)
from cyberfusion.ClusterSupport.tests_factories import BaseBackendFactory


class ServiceAccountToClusterFactory(BaseBackendFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        model = ServiceAccountToCluster

        exclude = (
            "service_account",
            "cluster",
        )

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    service_account = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_accounts.ServiceAccountFactory",
    )
    service_account_id = factory.SelfAttribute("service_account.id")
