import json
from pathlib import Path
from typing import Any, Dict, List


from helix_personmatching.mergers.merge_config import (
    MergeConfig,
    DataSetConfig,
    MergeRule,
)
from helix_personmatching.mergers.practitioner_merger import PractitionerMerger


def test_practitioner_merge() -> None:
    print()
    data_dir: Path = Path(__file__).parent.joinpath("./fixtures")

    with open(data_dir.joinpath("practitioner1.json")) as file:
        practitioner1_text = file.read()

    practitioner1 = json.loads(practitioner1_text)

    config: MergeConfig = MergeConfig(
        data_sets=[
            DataSetConfig(access_tag="medstar", merge_rule=MergeRule.Exclusive),
            DataSetConfig(access_tag="bwell", merge_rule=MergeRule.Exclusive),
        ]
    )

    result: Dict[str, Any] = PractitionerMerger().merge(
        row=practitioner1, config=config
    )
    fix_time_zone_in_resources(result["practitioner"])
    assert result["practitioner"][0] == practitioner1["practitioner"][0]

    result_practitioner_roles = result["practitionerrole"]
    fix_time_zone_in_resources(result_practitioner_roles)
    assert len(result_practitioner_roles) == 2
    assert result_practitioner_roles == practitioner1["practitionerrole"][:2]


def fix_time_zone_in_resources(resources: List[Dict[str, Any]]) -> None:
    for resource in resources:
        resource["meta"]["lastUpdated"] = resource["meta"]["lastUpdated"].replace(
            "+00:00", ".000Z"
        )
