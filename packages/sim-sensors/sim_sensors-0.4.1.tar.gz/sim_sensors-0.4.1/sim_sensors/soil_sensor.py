import random
from enum import Enum


class SoilState(Enum):
    AIR = 1
    DRY = 2
    MOIST = 3
    WATER = 4


def get_soil_moisture_level():
    #return a tumple consisting of an integer value and an enum value that describe
    # the moisture in the soil
    current = random.randint(1,1000)
    if current >= 1000:
        state = SoilState.AIR
    elif current < 1000 and current >= 600:
        state = SoilState.DRY
    elif current < 600 and current >= 370:
        state = SoilState.MOIST
    else:
        state = SoilState.WATER

    return current, state