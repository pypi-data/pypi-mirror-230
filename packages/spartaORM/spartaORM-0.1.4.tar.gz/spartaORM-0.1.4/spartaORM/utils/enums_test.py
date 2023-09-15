import unittest
from parameterized import parameterized

from spartaORM.enums.swim import (
    PoolType,
    AgeGroup,
    StrokeType,
    SwimType,
    RelayLeg,
    RelayType,
)
from spartaORM.utils.enums import (
    str_to_pool_type,
    str_to_age_group,
    str_to_relay_leg,
    str_to_relay_type,
    str_to_stroke_type,
    str_to_swim_type,
)


class TestStrToPoolType(unittest.TestCase):
    @parameterized.expand(
        [("LCM", PoolType.LCM), ("SCM", PoolType.SCM), ("SCY", PoolType.SCY)]
    )
    def test_str_to_pool_type(self, name, expected):
        self.assertEqual(str_to_pool_type(name), expected)


class TestStrToAgeGroup(unittest.TestCase):
    @parameterized.expand(
        [
            ("13", AgeGroup.Under13),
            ("14", AgeGroup.Under14),
            ("15", AgeGroup.Under15),
            ("16", AgeGroup.Under16),
            ("Open", AgeGroup.AgeOpen),
            ("17", AgeGroup.Age17AndAbove),
        ]
    )
    def test_str_to_age_group(self, name, expected):
        self.assertEqual(str_to_age_group(name), expected)


class TestStrToRelayLeg(unittest.TestCase):
    @parameterized.expand(
        [
            ("1", RelayLeg.Leg1),
            ("1", RelayLeg.Leg1),
            (2, RelayLeg.Leg2),
            (3, RelayLeg.Leg3),
        ]
    )
    def test_str_to_relay_leg(self, name, expected):
        self.assertEqual(str_to_relay_leg(name), expected)


class TestStrToRelayType(unittest.TestCase):
    @parameterized.expand(
        [
            ("Freestyle Relay", RelayType.FreestyleRelay),
            ("Medley Relay", RelayType.MedleyRelay),
            ("Mixed Freestyle Relay", RelayType.MixedFreestyleRelay),
        ]
    )
    def test_str_to_relay_type(self, name, expected):
        self.assertEqual(str_to_relay_type(name), expected)


class TestStrToStrokeType(unittest.TestCase):
    @parameterized.expand(
        [
            ("Freestyle", StrokeType.Freestyle),
            ("Backstroke", StrokeType.Backstroke),
            ("Breaststroke", StrokeType.Breaststroke),
            ("Individual Medley", StrokeType.IndividualMedley),
        ]
    )
    def test_str_to_stroke_type(self, name, expected):
        self.assertEqual(str_to_stroke_type(name), expected)


class TestStrToPoolType(unittest.TestCase):
    @parameterized.expand(
        [
            ("Final", SwimType.Final),
            ("Time Trial", SwimType.TimeTrial),
            ("Skins R2", SwimType.SkinsR2),
            ("Skins R1", SwimType.SkinsR1),
            ("Other 1", SwimType.Other1),
            ("C Final", SwimType.CFinal),
            ("Heat", SwimType.Heat),
        ]
    )
    def test_str_to_swim_type(self, name, expected):
        self.assertEqual(str_to_swim_type(name), expected)
