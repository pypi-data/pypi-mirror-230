import json
import random

from autonomous import log
from autonomous.apis import OpenAI
from autonomous.storage.cloudinarystorage import CloudinaryStorage
from slugify import slugify

from dmtoolkit.apis import DnDBeyondAPI
from dmtoolkit.models.dndobject import DnDObject


class Character(DnDObject):
    attributes = {
        # character traits
        "npc": True,
        "canon": False,
        "dnd_beyond_id": None,
        "name": "",
        "gender": "",
        "image": {"url": "", "asset_id": 0, "raw": None},
        "ac": 0,
        "desc": "",
        "backstory": "",
        "gender": "",
        "personality": "",
        "occupation": "",
        "race": "",
        "speed": {},
        "class_name": "",
        "age": 0,
        "hp": 0,
        "wealth": [],
        "inventory": [],
        "str": 0,
        "dex": 0,
        "con": 0,
        "wis": 0,
        "int": 0,
        "cha": 0,
        "features": {},
        "spells": {},
        "resistances": [],
        "chats": [],
        "conversation_summary": {"summary": "", "message": "", "response": ""},
        "backstory_summary": "",
    }

    def dndbeyond_updates(self):
        if not self.dnd_beyond_id:
            log("Player must have a dnd_id")
            return None
        else:
            data = DnDBeyondAPI.getcharacter(self.dnd_beyond_id)

            if results := self.table().find(dnd_id=self.dnd_beyond_id):
                self.pk = results["pk"]

            if data["image"]["url"] and data["image"]["url"] != self.image.get("url"):
                self.image = CloudinaryStorage().save(
                    data["image"]["url"], folder=f"dnd/players/{slugify(self.name)}"
                )
            del data["image"]
            self.__dict__.update(data)
        return data

    def get_image_prompt(self):
        style = ["Italian Renaissance", "John Singer Sargent", "James Tissot"]
        return f"A full color portrait in the style of {random.choice(style)} of a {self.race} character from Dungeons and Dragons aged {self.age} and described as {self.desc}"

    def chat(self, message):
        if not self.backstory_summary:
            self.backstory_summary = OpenAI().summarize_text(
                self.backstory,
                primer="Summarize the following text into 10 sentences or less. The text is a backstory for a D&D character.",
            )
        primer = "You are playing the role of a D&D NPC talking to a PC."
        prompt = "As D&D NPC matching the following description:"
        prompt += f"""
PERSONALITY: {", ".join(self.personality)}

DESCRIPTION: {self.desc}

BACKSTORY: {self.backstory_summary}
"""
        if self.conversation_summary["summary"]:
            prompt += f"""
CONTEXT: {self.conversation_summary['summary']}
"""
        prompt += """
Respond to the player's message below as the above described character
        """
        if self.conversation_summary["summary"]:
            prompt += "using the CONTEXT as a starting point"
        prompt += f"""
{message}
        """
        response = OpenAI().generate_text(prompt, primer)

        primer = "As an expert AI in D&D Worldbuilding as well, read the following dialogue. The first paragraph contains the context of the conversation, followed by the Player's message and then the NPC's response. Summarize into a concise paragraph, creating a readable summary that could help a person understand the main points of the conversation. Avoid unnecessary details."
        updated_summary = f"Previous conversation:\n{self.conversation_summary['summary']}\n\nPlayer Message:\n{self.conversation_summary['message']}\n\nNPC Response:\n{self.conversation_summary['response']}"
        self.conversation_summary["summary"] = OpenAI().summarize_text(
            updated_summary, primer=primer
        )
        self.conversation_summary["message"] = message
        self.conversation_summary["response"] = response
        self.save()
        return response

    @classmethod
    def generate(cls, name=None, summary=None, generate_image=False):
        age = random.randint(15, 45)
        personality = [
            "shy",
            "outgoing",
            "friendly",
            "mean",
            "snooty",
            "aggressive",
            "sneaky",
            "greedy",
            "kind",
            "generous",
            "smart",
            "dumb",
            "loyal",
            "dishonest",
            "honest",
            "lazy",
            "hardworking",
            "stubborn",
            "flexible",
            "proud",
            "humble",
            "confident",
            "insecure",
            "courageous",
            "cowardly",
            "optimistic",
            "pessimistic",
            "silly",
            "serious",
            "sensitive",
            "insensitive",
            "creative",
            "imaginative",
            "practical",
            "logical",
            "intuitive",
            "intelligent",
            "wise",
            "foolish",
            "curious",
            "nosy",
            "adventurous",
            "cautious",
            "careful",
            "reckless",
            "careless",
            "patient",
            "impatient",
            "tolerant",
            "intolerant",
            "forgiving",
            "unforgiving",
            "honest",
            "unfriendly",
            "outgoing",
            "shy",
            "sneaky",
            "honest",
            "dishonest",
            "disloyal",
            "unfriendly",
        ]

        gender = random.choices(
            ["male", "female", "non-binary"], weights=[5, 5, 1], k=1
        )[0]
        primer = """
        You are a D&D 5e NPC generator that creates interesting random NPC's with complete stats and backstory
        """
        traits = ", ".join(random.sample(personality, 3))
        if summary:
            prompt = f"Generate an Dungeons and Dragons style {gender} NPC aged {age} years who is {summary}. Write a detailed NPC backstory that contains an unexpected twist or secret. The NPC should also have the following personality traits: {traits}"
        else:
            prompt = f"Generate an Dungeons and Dragons style {gender} NPC aged {age} years with the following personality traits: {traits}. Include a backstory that contains an unexpected twist or secret"
        # log(prompt)
        funcobj = {
            "name": "generate_npc",
            "description": "builds NPC data object",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The character's name",
                    },
                    "age": {
                        "type": "integer",
                        "description": "The character's age",
                    },
                    "gender": {
                        "type": "string",
                        "description": "The character's gender",
                    },
                    "race": {
                        "type": "string",
                        "description": "The character's race",
                    },
                    "personality": {
                        "type": "array",
                        "description": "The character's personality traits",
                        "items": {"type": "string"},
                    },
                    "desc": {
                        "type": "array",
                        "description": "A physical description of the character",
                        "items": {"type": "string"},
                    },
                    "backstory": {
                        "type": "string",
                        "description": "The character's backstory",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The character's DnD class",
                    },
                    "occupation": {
                        "type": "string",
                        "description": "The character's daily occupation",
                    },
                    "inventory": {
                        "type": "array",
                        "description": "The character's inventory of items",
                        "items": {"type": "string"},
                    },
                    "str": {
                        "type": "number",
                        "description": "The amount of Strength the character has from 1-20",
                    },
                    "dex": {
                        "type": "integer",
                        "description": "The amount of Dexterity the character has from 1-20",
                    },
                    "con": {
                        "type": "integer",
                        "description": "The amount of Constitution the character has from 1-20",
                    },
                    "int": {
                        "type": "integer",
                        "description": "The amount of Intelligence the character has from 1-20",
                    },
                    "wis": {
                        "type": "integer",
                        "description": "The amount of Wisdom the character has from 1-20",
                    },
                    "cha": {
                        "type": "integer",
                        "description": "The amount of Charisma the character has from 1-20",
                    },
                },
            },
        }
        required = funcobj["parameters"]["properties"].keys()
        funcobj["parameters"]["required"] = list(required)
        response = OpenAI().generate_text(prompt, primer, functions=funcobj)
        try:
            npc_data = json.loads(response)
        except Exception as e:
            log(e)
            raise Exception(response)

        npc = cls(**npc_data)
        return npc
