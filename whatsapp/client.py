import requests
from config import TOKEN, VERSION, PHONE_NUMBER_ID


class WhatsAppClient:
    BASE_URL = f"https://graph.facebook.com/{VERSION}"

    @staticmethod
    def send_message(payload: dict) -> dict:
        url = f"{WhatsAppClient.BASE_URL}/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
