from core.interfaces import Questao


class MultiplaEscolha(Questao):
    def __init__(self, text: str, options: list[str], correct: int):
        super().__init__(text)
        self.options = options
        self.correct = correct

    def to_payload(self, to: str) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": self.text},
                "action": {
                    "button": "Escolher",
                    "sections": [{
                        "title": "Opções",
                        "rows": [
                            {"id": f"opt_{i}", "title": opt, "description": ""}
                            for i, opt in enumerate(self.options, 1)
                        ]
                    }]
                }
            }
        }
