import json
from pathlib import Path
from typing import Any, Dict

from helix_personmatching.mergers.practitioner_merger import PractitionerMerger


def test_practitioner_merge() -> None:
    print()
    data_dir: Path = Path(__file__).parent.joinpath("./fixtures")

    with open(data_dir.joinpath("practitioner1.json")) as file:
        practitioner1_text = file.read()

    practitioner1 = json.loads(practitioner1_text)

    result: Dict[str, Any] = PractitionerMerger().merge(row=practitioner1, config=None)
    practitioner1["practitioner"][0]["meta"][
        "lastUpdated"
    ] = "2023-03-30T10:53:17+00:00"
    assert result["practitioner"][0] == practitioner1["practitioner"][0]
