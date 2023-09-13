import dataclasses
from enum import Enum

from typing import List


class MergeRule(Enum):
    ignore = 1
    exclusive = 2
    merge = 3


@dataclasses.dataclass
class DataSetConfig:
    access_tag: str
    merge_rule: MergeRule


@dataclasses.dataclass
class MergeConfig:
    data_sets: List[DataSetConfig]
