from enum import Enum


class Directions(Enum):
    GET = 0
    SET = 1


def reversed_direction(direction: Directions):
    return Directions.SET if direction == Directions.GET else Directions.GET
