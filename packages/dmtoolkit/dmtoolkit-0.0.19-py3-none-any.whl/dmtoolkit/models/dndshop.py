from autonomous.model.automodel import AutoModel
from .dndcharacter import Character
from autonomous import log
import json
from autonomous.apis import OpenAI
from autonomous.storage.cloudinarystorage import CloudinaryStorage


class Shop(AutoModel):
    attributes = {
        "name": "",
        "image": {"url": "", "asset_id": 0, "raw": None},
        "shoptype": "",
        "owner": None,
        "inventory": {},
        "location": "",
        "desc": "",
    }

    def generate_image(self):
        resp = OpenAI().generate_image(
            self.get_image_prompt(),
            n=1,
        )
        folder = f"dnd/{self.__class__.__name__.lower()}s"
        self.image = CloudinaryStorage().save(resp[0], folder=folder)
        self.save()

    def get_image_prompt(self):
        description = self.desc or "A simple general goods shop with wooden counters and shelves."

        return f"A full color interior image of a medieval fantasy merchant shop called {self.name} with the following description: {description}"

    @classmethod
    def generate(cls):
        primer = """
        You are a D&D 5e Shop generator that creates random shops.
        """
        prompt = "Generate a random shop"
        funcobj = {
            "name": "generate_shop",
            "description": "builds an Shop model object",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The shop's name",
                    },
                    "shoptype": {
                        "type": "string",
                        "description": "The type of wares the shop sells",
                    },
                    "desc": {
                        "type": "string",
                        "description": "A short description of the inside of the shop",
                    },
                    "inventory": {
                        "type": "array",
                        "description": "The shop's inventory of purchasable items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The name of the item",
                                },
                                "desc": {
                                    "type": "string",
                                    "description": "A short description of the item",
                                },
                                "cost": {
                                    "type": "string",
                                    "description": "the cost of the item",
                                },
                            },
                        },
                    },
                },
            },
        }

        funcobj["parameters"]["required"] = list(funcobj["parameters"]["properties"].keys())
        shop = OpenAI().generate_text(prompt, primer, functions=funcobj)
        try:
            shop = json.loads(shop)
        except Exception as e:
            log(e)
            return None
        else:
            shopowner = Character.generate(summary=f"Owner of {shop['name']}, a {shop['shoptype']} shop.")
            shopowner.save()
            shop["owner"] = shopowner
            shop_obj = Shop(**shop)
            shop_obj.save()
        return shop_obj
