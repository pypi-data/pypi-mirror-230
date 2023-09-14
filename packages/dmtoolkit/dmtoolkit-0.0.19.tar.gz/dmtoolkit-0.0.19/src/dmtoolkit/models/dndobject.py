from dmtoolkit.apis import open5eapi

from autonomous.apis import OpenAI
from autonomous.storage.cloudinarystorage import CloudinaryStorage
from autonomous.model.automodel import AutoModel
from autonomous import log

from slugify import slugify


class DnDObject(AutoModel):
    _storage = CloudinaryStorage()
    search_api = None

    @property
    def slug(self):
        return slugify(self.name)

    def save(self):
        if self.image.get("raw"):
            folder = f"dnd/{self.__class__.__name__.lower()}s/{self.slug}"
            self.image = self._storage.save(self.image["raw"], folder=folder)
        return super().save()

    @classmethod
    def search(cls, **kwargs):
        results = super().search(**kwargs)
        if cls.search_api:
            names = [obj.name for obj in results]
            api_results = cls.search_api.search(list(kwargs.values()))
            for obj in api_results:
                if obj["name"] not in names:
                    o = cls(**obj)
                    o.save()
                    results.append(o)
                    names.append(o.name)
        return results

    def generate_image(self):
        resp = OpenAI().generate_image(
            self.get_image_prompt(),
            n=1,
        )
        folder = f"dnd/{self.__class__.__name__.lower()}s"
        self.image = self._storage.save(resp[0], folder=folder)
        return self.save()

    def get_image_prompt(self):
        return f"A full color portrait of a {self.name} from Dungeons and Dragons 5e - {self.desc}"
