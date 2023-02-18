import requests

from horde.logger import logger
from horde.threads import PrimaryTimedFunction

class ModelReference(PrimaryTimedFunction):
    quorum = None
    reference = None
    text_reference = None
    stable_diffusion_names = set()
    text_model_names = set()
    nsfw_models = set()
    controlnet_models = set()

    def call_function(self):
        '''Retrieves to nataili and text model reference and stores in it a var'''
        # If it's running in SQLITE_MODE, it means it's a test and we never want to grab the quorum
        # We don't want to report on any random model name a client might request
        try:
            self.reference = requests.get("https://raw.githubusercontent.com/Sygil-Dev/nataili-model-reference/main/db.json", timeout=2).json()
            # logger.debug(self.reference)
            self.stable_diffusion_names = set()
            for model in self.reference:
                if self.reference[model].get("baseline") in {"stable diffusion 1","stable diffusion 2"}:
                    self.stable_diffusion_names.add(model)
                    if self.reference[model].get("nsfw"):
                        self.nsfw_models.add(model)
                    if self.reference[model].get("type") == "controlnet":
                        self.controlnet_models.add(model)
        except Exception:
            logger.error(f"Error when downloading nataili models list: {e}")
        try:
            self.text_reference = requests.get("https://raw.githubusercontent.com/db0/AI-Horde-text-model-reference/main/db.json", timeout=2).json()
            # logger.debug(self.reference)
            self.text_model_names = set()
            for model in self.text_reference:
                self.text_model_names.add(model)
                if self.text_model_names[model].get("nsfw"):
                    self.nsfw_models.add(model)

        except Exception:
            logger.error(f"Error when downloading known models list: {e}")

    def get_model_names(self):
        return set(reference.keys())


model_reference = ModelReference(3600, None)