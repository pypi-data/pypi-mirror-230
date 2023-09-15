from enum import Enum


class StrokeType(Enum):
    Freestyle = "Freestyle"
    Breaststroke = "Breaststroke"
    Backstroke = "Backstroke"
    Butterfly = "Butterfly"
    IndividualMedley = "Individual Medley"


class SwimType(Enum):
    Final = "Final"
    SemiFinal = "Semi Final"
    Heat = "Heat"
    BFinal = "B Final"
    CFinal = "C Final"
    SwimOff = "Swim Off"
    TimeTrial = "Time Trial"
    Training = "Training"
    SkinsR1 = "Skins R1"
    SkinsR2 = "Skins R2"
    SkinsR3 = "Skins R3"
    Other1 = "Other 1"
    Other2 = "Other 2"


class PoolType(Enum):
    LCM = "LCM"
    SCM = "SCM"
    SCY = "SCY"


class AgeGroup(Enum):
    Under13 = "Under 13"
    Under14 = "Under 14"
    Under15 = "Under 15"
    Under16 = "Under 16"
    Age17AndAbove = "Age 17+"
    AgeOpen = "Age Open"


class RelayType(Enum):
    FreestyleRelay = "Freestyle Relay"
    MedleyRelay = "Medley Relay"
    MixedFreestyleRelay = "Mixed Freestyle Relay"
    MixedMedleyRelay = "Mixed Medley Relay"


class RelayLeg(Enum):
    Leg1 = "Leg 1"
    Leg2 = "Leg 2"
    Leg3 = "Leg 3"
    Leg4 = "Leg 4"
