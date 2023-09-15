import requests


def tg_send(message, conf):
    TOKEN = conf["telegram_token"]
    CHAT_ID = conf["telegram_chat_ID"]
    apiURL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        response = requests.post(apiURL, json={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(e)
