from typing import Any, Dict, Optional

from helix_personmatching.mergers.merge_config import MergeConfig
from helix_personmatching.mergers.merge_struct import MergeStruct


class PractitionerMerger:
    # noinspection PyMethodMayBeStatic
    def merge(
        self, row: Dict[str, Any], config: Optional[MergeConfig]
    ) -> Dict[str, Any]:
        print("PractitionerMerger.merge")
        merge_struct = MergeStruct(row)
        print(merge_struct.to_dict())
        return merge_struct.to_dict()
