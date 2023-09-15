import os
import sys
shell_dir = os.path.dirname(os.path.realpath(__file__))
ezrename_dir = os.path.dirname(shell_dir)

base_dir = os.path.join(ezrename_dir, ".")
sys.path.append(base_dir)

from spartaORM.controller.athlete import Athlete
from spartaORM.enums.sex import Sex

athlete_controller = Athlete(database_url="postgresql://sparta:sparta@localhost:5432/sparta-local")

# added = athlete_controller.add(id=12112, user_name="Arsun", first_name="A2run", last_name="Ku2mar", sex=Sex.male, known_as="Arun")

fetched = athlete_controller.fetch_athlete()

for athlete in fetched:
    print(athlete.user_name)

print("fetched : ", fetched)