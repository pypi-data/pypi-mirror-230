from typing_extensions import TypedDict

from app.types.enums.ams_property import RELAY_TYPE


class LapTime(TypedDict):
    time: str
    distance: str
    splitTime: str


class CalculationPayload(TypedDict):
    relay_type: RELAY_TYPE
    pool_length: int
    frame_rate: int
    lap_times: list
    distance: int
