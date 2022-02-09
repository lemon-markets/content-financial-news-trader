# Importing libraries
import requests
import os
import json


class Telegram:
    def __init__(self):
        self.token: str = os.environ.get("telegram_token")
        self.chatID: str = os.environ.get("telegram_chatID")


    def send_message(self, bot_message: str):

        send_text = 'https://api.telegram.org/bot' + self.token + '/sendMessage?chat_id=' + self.chatID + '&parse_mode=Markdown&text=' + json.dumps(bot_message)
        response = requests.get(send_text)

        return response.json()