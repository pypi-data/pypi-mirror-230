from typing import Union
from spartaORM.enums.swim import (
    PoolType,
    StrokeType,
    RelayLeg,
    RelayType,
    SwimType,
    AgeGroup,
)


def fetch_enum(enum, value: str):
    for type in enum:
        if type.value == value:
            return type


def str_to_pool_type(type: str):
    enum_value = fetch_enum(PoolType, type)

    if enum_value != None:
        return enum_value

    raise Exception(f"Pool type {type} is not found.")


def str_to_stroke_type(type: str):
    enum_value = fetch_enum(StrokeType, type)

    if enum_value != None:
        return enum_value

    raise Exception(f"Stroke type {type} is not found.")


def str_to_relay_leg(type: Union[str, int]):
    for leg in RelayLeg:
        if str(type) in leg.value:
            return leg

    raise Exception(f"Relay leg {type} is not found.")


def str_to_relay_type(type: str):
    enum_value = fetch_enum(RelayType, type)

    if enum_value != None:
        return enum_value

    raise Exception(f"Relay type {type} is not found.")


def str_to_swim_type(type: str):
    enum_value = fetch_enum(SwimType, type)

    if enum_value != None:
        return enum_value

    raise Exception(f"Swim type {type} is not found.")


def str_to_age_group(type: str):
    for group in AgeGroup:
        if type in group.value:
            return group

    raise Exception(f"Age group {type} is not found.")
