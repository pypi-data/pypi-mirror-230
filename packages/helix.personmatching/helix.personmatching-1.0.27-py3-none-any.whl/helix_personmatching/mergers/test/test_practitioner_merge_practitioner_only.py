import json
from pathlib import Path
from typing import Any, Dict, List

from fhir.resources.R4B.practitioner import Practitioner

from helix_personmatching.mergers.merge_config import (
    MergeConfig,
    DataSetConfig,
    MergeRule,
)
from helix_personmatching.mergers.practitioner_merger import PractitionerMerger


def test_practitioner_merge_practitioner_only() -> None:
    print()
    data_dir: Path = Path(__file__).parent.joinpath("./fixtures")

    with open(data_dir.joinpath("practitioner1.json")) as file:
        practitioner1_text = file.read()

    practitioner1_dict: Dict[str, Any] = json.loads(practitioner1_text)

    practitioner1: Practitioner = Practitioner.parse_obj(
        practitioner1_dict["practitioner"][0]
    )

    config: MergeConfig = MergeConfig(
        data_sets=[
            DataSetConfig(access_tag="medstar", merge_rule=MergeRule.Exclusive),
            DataSetConfig(access_tag="bwell", merge_rule=MergeRule.Exclusive),
        ]
    )

    result: Practitioner = PractitionerMerger().merge_practitioner(
        practitioner=practitioner1, config=config
    )
    assert result.dict() == practitioner1


def fix_time_zone_in_resources(resources: List[Dict[str, Any]]) -> None:
    for resource in resources:
        resource["meta"]["lastUpdated"] = resource["meta"]["lastUpdated"].replace(
            "+00:00", ".000Z"
        )
