from kaya_module_sdk.types.datapoint.KTimeSeries import KTimeSeries
from kaya_module_sdk.types.primitives.KString import KString
from kaya_module_sdk.types.primitives.KFloat import KFloat


class KFloatDatapoint(KTimeSeries):

    def __init__(self, data: list[KString, KFloat]):
        invalid_values = [
            item[1] for item in data if not isinstance(item[1], KFloat)
        ]
        if invalid_values:
            raise TypeError(
                f'KTSFloat can only have KFloat values! Not ({invalid_values})'
            )
        super().__init__(data)
