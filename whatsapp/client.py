import requests
from config import TOKEN, VERSION, PHONE_NUMBER_ID
from logger import logger


class WhatsAppClient:
    BASE_URL = f"https://graph.facebook.com/{VERSION}"

    @staticmethod
    def send_message(to: str = None, text: str = None, is_questao: bool = False, payload: dict = None) -> dict:

        if is_questao:
            payload = payload
        else:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {"body": text}
            }

        response = requests.post(
            f"{WhatsAppClient.BASE_URL}/{PHONE_NUMBER_ID}/messages",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        response.raise_for_status()

        try:
            # Para mensagens de texto simples, apenas use 'text'
            logger.log_message(usuario=to, mensagem=text, direcao="enviada")
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

        return response.json()

    @staticmethod
    def send_button_message(to: str, body_text: str, buttons: list) -> dict:
        """
        Envia uma mensagem do tipo button.
        :param to: número do destinatário
        :param body_text: texto da mensagem
        :param buttons: lista de dicts, ex: [{"id": "btn1", "title": "Opção 1"}, {"id": "btn2", "title": "Opção 2"}]
        """
        if len(buttons) > 3:
            raise ValueError("O WhatsApp permite no máximo 3 botões por mensagem.")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"]}}
                        for btn in buttons
                    ]
                }
            }
        }

        logger.log_message(usuario=to, mensagem=body_text, direcao="enviada")

        return WhatsAppClient.send_message(payload=payload, is_questao=True)
