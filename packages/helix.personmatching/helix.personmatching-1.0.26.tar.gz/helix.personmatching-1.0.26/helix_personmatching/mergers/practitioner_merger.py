from typing import Any, Dict, Optional, List, cast

from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.domainresource import DomainResource
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.practitionerrole import PractitionerRole

from helix_personmatching.mergers.merge_config import MergeConfig, MergeRule
from helix_personmatching.mergers.merge_struct import MergeStruct


class PractitionerMerger:
    # noinspection PyMethodMayBeStatic
    def merge(
        self, row: Dict[str, Any], config: Optional[MergeConfig]
    ) -> Dict[str, Any]:
        merge_struct = MergeStruct(row)
        merge_struct.practitioner_roles = cast(
            List[PractitionerRole],
            self.merge_resources(
                resources=cast(List[DomainResource], merge_struct.practitioner_roles),
                config=config,
            ),
        )
        return merge_struct.to_dict()

    def merge_resources(
        self, resources: List[DomainResource], config: Optional[MergeConfig]
    ) -> List[DomainResource]:
        assert config
        combined_resources: List[DomainResource] = []
        for data_set in config.data_sets:
            # if there are resources available for this data set then filter to those and return
            resources_for_data_set: List[
                DomainResource
            ] = self.filter_resources_by_access_tag(
                resources=resources, access_tag=data_set.access_tag
            )
            if data_set.merge_rule == MergeRule.Ignore:
                # for ignore rule, just skip all resources for this dataset
                continue
            if data_set.merge_rule == MergeRule.Exclusive:
                # for exclusive rule, ignore any resources from other data sets
                if len(resources_for_data_set) > 1:
                    return resources_for_data_set
            if data_set.merge_rule == MergeRule.Merge:
                # for merge rule, combine these resources with the others
                combined_resources.extend(resources_for_data_set)

        return combined_resources

    # noinspection PyMethodMayBeStatic
    def filter_resources_by_access_tag(
        self, resources: List[DomainResource], access_tag: str
    ) -> List[DomainResource]:
        filter_resources: List[DomainResource] = []
        for resource in resources:
            security_tags: List[Coding] = cast(
                List[Coding], cast(Meta, resource.meta).security
            )
            access_tags: List[str] = [
                security_tag.code
                for security_tag in security_tags
                if security_tag.system == "https://www.icanbwell.com/access"
            ]
            if access_tag in access_tags:
                filter_resources.append(resource)
        return filter_resources
