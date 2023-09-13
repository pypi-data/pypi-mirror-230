import dataclasses
from enum import Enum

from typing import List


class MergeRule(Enum):
    Ignore = 1
    Exclusive = 2
    Merge = 3


@dataclasses.dataclass
class DataSetConfig:
    access_tag: str
    merge_rule: MergeRule


@dataclasses.dataclass
class MergeConfig:
    data_sets: List[DataSetConfig]
