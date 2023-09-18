"""Factories for API object."""

from typing import Any, Dict, List, Optional

import factory
import factory.fuzzy

from cyberfusion.ClusterSupport.clusters import (
    Cluster,
    ClusterGroup,
    UNIXUserHomeDirectory,
)
from cyberfusion.ClusterSupport.tests_factories import BaseBackendFactory


class ClusterFactory(BaseBackendFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        model = Cluster

        exclude = ("customer",)

    customer = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.customers.CustomerFactory",
    )
    customer_id = factory.SelfAttribute("customer.id")
    php_ioncube_enabled: bool = False
    php_sessions_spread_enabled: bool = False
    kernelcare_license_key: Optional[str] = None
    wordpress_toolkit_enabled: bool = False
    malware_toolkit_enabled: bool = False
    sync_toolkit_enabled: bool = False
    bubblewrap_toolkit_enabled: bool = False
    malware_toolkit_scans_enabled: bool = False
    database_toolkit_enabled: bool = False
    description: Optional[str] = None
    unix_users_home_directory: Optional[str] = None
    php_versions: List[str] = []
    redis_password: Optional[str] = None
    postgresql_backup_interval: Optional[int] = None
    mariadb_backup_interval: Optional[int] = None
    mariadb_cluster_name: Optional[str] = None
    redis_memory_limit: Optional[int] = None
    mariadb_version: Optional[str] = None
    postgresql_version: Optional[int] = None
    nodejs_version: Optional[int] = None
    nodejs_versions: List[str] = []
    custom_php_modules_names: List[str] = []
    php_settings: Dict[str, Any] = {}
    automatic_borg_repositories_prune_enabled: bool = False
    groups: List[str] = []


class ClusterWebFactory(ClusterFactory):
    """Factory for specific object."""

    groups = [ClusterGroup.WEB]
    unix_users_home_directory = factory.fuzzy.FuzzyChoice(
        UNIXUserHomeDirectory
    )
    php_versions = ["8.1", "8.0", "7.4", "7.3", "7.2", "7.1", "7.0", "5.6"]
    nodejs_versions = ["14.0"]
    nodejs_version = 18


class ClusterRedirectFactory(ClusterFactory):
    """Factory for specific object."""

    groups = [ClusterGroup.REDIRECT]


class ClusterDatabaseFactory(ClusterFactory):
    """Factory for specific object."""

    groups = [ClusterGroup.DB]
    mariadb_version = "10.10"
    postgresql_version = 15
    mariadb_cluster_name = factory.Faker(
        "password",
        special_chars=False,
        upper_case=False,
        digits=False,
    )
    redis_password = factory.Faker("password", special_chars=False, length=24)
    redis_memory_limit = factory.Faker("random_int", min=32, max=1024)
    mariadb_backup_interval = factory.Faker("random_int", min=4, max=24)
    postgresql_backup_interval = factory.Faker("random_int", min=4, max=24)


class ClusterMailFactory(ClusterFactory):
    """Factory for specific object."""

    groups = [ClusterGroup.MAIL]
    unix_users_home_directory = UNIXUserHomeDirectory.MNT_MAIL


class ClusterBorgClientFactory(ClusterFactory):
    """Factory for specific object."""

    groups = [ClusterGroup.BORG_CLIENT, ClusterGroup.WEB]
    unix_users_home_directory = factory.fuzzy.FuzzyChoice(
        UNIXUserHomeDirectory
    )


class ClusterBorgServerFactory(ClusterFactory):
    """Factory for specific object."""

    groups = [ClusterGroup.BORG_SERVER]
    unix_users_home_directory = UNIXUserHomeDirectory.MNT_BACKUPS
