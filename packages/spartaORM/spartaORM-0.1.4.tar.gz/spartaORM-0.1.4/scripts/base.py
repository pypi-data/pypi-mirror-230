import os
import sys

from spartaORM.controller.athlete import Athlete


rename_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

base_dir = os.path.join(rename_dir, ".")
print(base_dir)
sys.path.append(base_dir)

class Base:
    def __init__(self):
        self.database_url="postgresql://sparta:sparta@localhost:5432/sparta-local"

    @property
    def athlete(self):
        return Athlete(database_url=self.database_url)