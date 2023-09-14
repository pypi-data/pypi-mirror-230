import os

from autonomous import log


class FoundryAPI:
    api_url = os.environ.get("FOUNDRY_URL", "http://localhost:30000/api")
