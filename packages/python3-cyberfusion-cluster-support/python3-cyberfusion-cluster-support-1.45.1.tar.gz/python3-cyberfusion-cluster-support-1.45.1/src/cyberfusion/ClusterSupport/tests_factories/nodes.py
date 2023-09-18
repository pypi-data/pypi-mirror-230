"""Factories for API object."""

from typing import Optional

import factory

from cyberfusion.ClusterSupport.nodes import Node, NodeGroup
from cyberfusion.ClusterSupport.tests_factories import BaseBackendFactory


class _NodeFactory(BaseBackendFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        model = Node

    comment = None
    load_balancer_health_checks_groups_pairs: dict = {}
    groups_properties: dict[str, Optional[dict]] = {
        "Redis": None,
        "MariaDB": None,
    }


class NodeRedisFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterDatabaseFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.REDIS]
    groups_properties = {
        "Redis": {"is_master": True},
        "MariaDB": None,
    }


class NodeHAProxyFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.HAPROXY]


class NodeMariaDBFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterDatabaseFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.MARIADB]
    groups_properties = {
        "MariaDB": {"is_master": True},
        "Redis": None,
    }


class NodePHPFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterWebFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.PHP]


class NodePostgreSQLFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterDatabaseFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.POSTGRESQL]


class NodeMainFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.MAIN]


class NodeApacheFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterWebFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.APACHE]


class NodeFastRedirectFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterRedirectFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.FAST_REDIRECT]


class NodeNginxFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterWebFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.NGINX]


class NodeDovecotFactory(_NodeFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        exclude = ("cluster",)

    cluster = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.clusters.ClusterMailFactory"
    )
    cluster_id = factory.SelfAttribute("cluster.id")
    groups = [NodeGroup.DOVECOT]
