from core.interfaces import Questao


class SomChoice(Questao):
    def __init__(self, text: str, audio_url: str, options: list[str], correct: int):
        super().__init__(text)
        self.audio_url = audio_url
        self.options = options
        self.correct = correct

    def to_payload(self, to: str) -> dict:
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "audio",
                    "audio": {"link": self.audio_url}
                },
                "body": {"text": self.text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": f"opt_{i}", "title": opt}
                        }
                        for i, opt in enumerate(self.options, 1)
                    ]
                }
            }
        }
