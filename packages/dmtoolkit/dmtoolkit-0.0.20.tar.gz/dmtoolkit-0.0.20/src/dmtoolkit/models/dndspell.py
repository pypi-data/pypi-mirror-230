from dmtoolkit.models.dndobject import DnDObject
from dmtoolkit.apis import spell_api
from autonomous import logger
import random


class Spell(DnDObject):
    search_api = spell_api
    attributes = {
        "name": "",
        "image": {"url": "", "asset_id": 0, "raw": None},
        "desc": "",
        "variations": "",
        "range": 0,
        "ritual": False,
        "duration": 0,
        "concentration": False,
        "casting_time": "",
        "level": 0,
        "school": "",
        "archetype": "",
        "circles": "",
        "damage_dice": "",
        "damage_type": "",
    }

    def get_image_prompt(self):
        description = self.desc or "A magical spell"
        style = random.choice(
            [
                "The Rusted Pixel style digital image",
                "Albrecht Dürer style photorealistic pencil sketch",
                "William Blake style watercolor",
            ]
        )
        return f"A full color {style} of the {self.name} spell in action from Dungeons and Dragons 5e - {description}"
