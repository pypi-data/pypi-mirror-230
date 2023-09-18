"""Factories for API object."""

import factory
import factory.fuzzy

from cyberfusion.ClusterSupport.service_accounts import (
    ServiceAccount,
    ServiceAccountGroup,
)
from cyberfusion.ClusterSupport.tests_factories import BaseBackendFactory


class ServiceAccountFactory(BaseBackendFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        model = ServiceAccount

    name = factory.Faker("domain_name")
    group = factory.fuzzy.FuzzyChoice(ServiceAccountGroup)
