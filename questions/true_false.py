from core.interfaces import Questao


class VerdadeiroFalso(Questao):
    def __init__(self, text: str, answer: bool):
        super().__init__(text)
        self.answer = answer

    def to_payload(self, to: str) -> dict:
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": self.text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": "true", "title": "Verdadeiro"}
                        },
                        {
                            "type": "reply",
                            "reply": {"id": "false", "title": "Falso"}
                        }
                    ]
                }
            }
        }
