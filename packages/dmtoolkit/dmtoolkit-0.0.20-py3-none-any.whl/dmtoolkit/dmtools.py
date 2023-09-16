import json
import random
from slugify import slugify
import dice
from autonomous.logger import log
from autonomous.apis import OpenAI
from dmtoolkit.models import Monster, Item, Spell, Character, Shop


class DMTools:
    """
    _summary_

    Returns:
        _type_: _description_
    """

    LOOT_MULTIPLIER = 3

    @classmethod
    def roll_dice(roll_str):
        return dice.roll(roll_str)

    @classmethod
    def updatedb(cls):
        Monster.update_db()
        Spell.update_db()
        Item.update_db()

    @classmethod
    def _query(cls, api, **kwargs):
        # log(api, kwargs)
        if "pk" in kwargs:
            results = [api.get(kwargs["pk"])]
        elif kwargs:
            kwargs["slug"] = slugify(kwargs.get("name", ""))
            results = api.search(**kwargs)
        else:
            results = api.all()
        return results

    @classmethod
    def monsters(cls, **kwargs):
        return cls._query(Monster, **kwargs)

    @classmethod
    def items(cls, **kwargs):
        return cls._query(Item, **kwargs)

    @classmethod
    def spells(cls, **kwargs):
        return cls._query(Spell, **kwargs)

    @classmethod
    def characters(cls, **kwargs):
        # log(kwargs)
        return cls._query(Character, **kwargs)

    @classmethod
    def pcs(cls, **kwargs):
        kwargs.update({"npc": False})
        return cls._query(Character, **kwargs)

    @classmethod
    def npcs(cls, **kwargs):
        kwargs.update({"npc": True})
        return cls._query(Character, **kwargs)

    @classmethod
    def shops(cls, **kwargs):
        return cls._query(Shop, **kwargs)

    @classmethod
    def generatenpc(cls, name=None, summary=None, generate_image=False):
        return Character.generate()

    @classmethod
    def generateencounter(cls, num_players=5, level=1):
        difficulty_list = [
            "trivial",
            "easy",
            "medium",
            "hard",
        ]
        loot = [
            "gold",
            "gems",
            "magic item",
            "junk",
            "weapon",
            "armor",
        ]

        primer = """
        You are a D&D 5e Encounter generator that creates level appropriate random encounters and specific loot rewards.
        """
        difficulty = random.choice(list(enumerate(difficulty_list)))
        loot_type = random.choices(
            loot,
            weights=[10, 5, 3, 30, 10, 10],
            k=(difficulty[0] * DMTools.LOOT_MULTIPLIER) + 1,
        )
        prompt = f"Generate an appropriate Dungeons and Dragons 5e encounter for a party of {num_players} at level {level} that is {difficulty[1]} and rewards the following type of loot items: {loot_type}"
        funcobj = {
            "name": "generate_encounter",
            "description": "Generate an Encounter object",
            "parameters": {
                "type": "object",
                "properties": {
                    "enemies": {
                        "type": "array",
                        "description": "A list of enemies faced in the encounter",
                        "items": {"type": "string"},
                    },
                    "scenario": {
                        "type": "string",
                        "description": "The situation that led to the encounter from the enemy's perspective",
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "The difficulty of the encounter",
                    },
                    "loot": {
                        "type": "array",
                        "description": "Loot gained from the encounter",
                        "items": {"type": "string"},
                    },
                },
            },
        }
        funcobj["parameters"]["required"] = list(
            funcobj["parameters"]["properties"].keys()
        )
        # breakpoint()
        encounter = OpenAI().generate_text(prompt, primer, functions=funcobj)
        encounter = json.loads(encounter)
        return encounter

    @classmethod
    def generateshop(cls):
        return Shop.generate()
