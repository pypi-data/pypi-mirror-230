import dataclasses
from enum import Enum

from typing import List, Optional


class MergeRule(Enum):
    Ignore = "ignore"
    Exclusive = "exclusive"
    Merge = "merge"


class FieldType(Enum):
    Name = "name"
    Address = "address"
    Phone = "phone"
    Language = "language"
    Photo = "photo"
    Qualification = "qualification"
    Identifier = "identifier"
    Specialty = "specialty"
    Insurance = "insurance"


@dataclasses.dataclass
class FieldRule:
    field: FieldType
    rule: MergeRule


@dataclasses.dataclass
class DataSetConfig:
    access_tag: str
    merge_rule: Optional[MergeRule]
    field_rules: Optional[List[FieldRule]] = None


@dataclasses.dataclass
class MergeConfig:
    data_sets: List[DataSetConfig]
