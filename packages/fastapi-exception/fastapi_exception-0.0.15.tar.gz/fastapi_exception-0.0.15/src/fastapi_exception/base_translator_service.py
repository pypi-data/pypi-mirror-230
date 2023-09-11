from abc import abstractmethod


class BastTranslatorService:
    @abstractmethod
    def translate(self, *kwargs):
        pass
