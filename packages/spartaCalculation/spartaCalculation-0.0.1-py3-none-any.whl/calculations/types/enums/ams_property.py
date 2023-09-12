from enum import Enum


class RELAY_TYPE(Enum):
    FREESTYLE_RELAY = "Freestyle Relay"
    MEDLEY_RELAY = "Medley Relay"
    MIXED_FREESTYLE_RELAY = "Mixed Freestyle Relay"
    MIXED_MEDLEY_RELAY = "Mixed Medley Relay"


class SWIM_TYPE(Enum):
    FINAL = "Final"
    SEMI_FINAL = "Semi Final"
    HEAT = "Heat"
    B_FINAL = "B Final"
    C_FINAL = "C Final"
