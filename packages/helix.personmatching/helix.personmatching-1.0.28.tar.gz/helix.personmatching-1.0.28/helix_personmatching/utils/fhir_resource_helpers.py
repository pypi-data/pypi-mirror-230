from typing import Dict, Any, List


class FhirResourceHelpers:
    @staticmethod
    def remove_none_values_from_dict_or_list(
        item: Dict[str, Any]
    ) -> Dict[str, Any] | List[Dict[str, Any]]:
        if isinstance(item, list):
            return [FhirResourceHelpers.remove_none_values_from_dict(i) for i in item]
        if not isinstance(item, dict):
            return item
        return {
            k: FhirResourceHelpers.remove_none_values_from_dict(v)
            for k, v in item.items()
            if v is not None and not (k == "extension" and isinstance(v, str))
        }

    @staticmethod
    def remove_none_values_from_dict(item: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(item, dict):
            return item
        return {
            k: FhirResourceHelpers.remove_none_values_from_dict_or_list(v)
            for k, v in item.items()
            if v is not None and not (k == "extension" and isinstance(v, str))
        }
