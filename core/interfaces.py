from abc import ABC, abstractmethod


class Questao(ABC):
    def __init__(self, text: str):
        self.text = text

    @abstractmethod
    def to_payload(self, to: str) -> dict:
        """Retorna o payload no formato aceito pela API do WhatsApp."""
        pass
