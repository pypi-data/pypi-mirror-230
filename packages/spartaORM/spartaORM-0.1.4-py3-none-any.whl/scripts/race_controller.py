import os
import sys
shell_dir = os.path.dirname(os.path.realpath(__file__))
ezrename_dir = os.path.dirname(shell_dir)

base_dir = os.path.join(ezrename_dir, ".")
sys.path.append(base_dir)

from spartaORM.controller.race import Race
from spartaORM.enums.swim import (
    SwimType,
    StrokeType,
    RelayLeg,
    RelayType,
    PoolType,
    AgeGroup,
)
from datetime import date


race_controller = Race(database_url="postgresql://sparta:sparta@localhost:5432/sparta-local")

added = race_controller.add(
    swim_date="12/12/2001",
    athlete_id=12112,
    event_id=12,
    competition_id="12",
    swim_type=SwimType.Final,
    stroke_type=StrokeType.Backstroke,
    relay_leg=RelayLeg.Leg1,
    relay_type=RelayType.FreestyleRelay,
    pool_type=PoolType.SCM,
    age_group=AgeGroup.AgeOpen,
    event_distance=50,
    created_time=date(year=2020, month=12, day=12),
    online_video_filename="adfkhb",
    venue_id="13",
    is_relay=False
)


print("added : ", added)