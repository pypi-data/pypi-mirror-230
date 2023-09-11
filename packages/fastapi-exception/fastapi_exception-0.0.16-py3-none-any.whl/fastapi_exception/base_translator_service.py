from abc import abstractmethod


class BaseTranslatorService:
    @abstractmethod
    def translate(self, *kwargs):
        pass
