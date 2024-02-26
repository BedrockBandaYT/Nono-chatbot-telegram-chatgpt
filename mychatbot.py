import requests
import json
import time

TELEGRAM_TOKEN = "6871811896:AAEdMOsg6-B5DqikpWuS2LCEqvwKOweX1z8"
OPENAI_API_KEY = "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"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def process_message(message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "text-davinci-002",
        "prompt": message,
        "max_tokens": 50
    }
    try:
        response = requests.post("https://api.openai.com/v1/engines/text-davinci-002/completions", headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad response status codes
        response_data = response.json()
        completion = response_data["choices"][0]["text"].strip()
        return completion
    except requests.exceptions.RequestException as e:
        print(f"Error processing message: {e}")
        return "Sorry, I encountered an error processing your message."

def handle_start(chat_id):
    send_message(chat_id, "Hi! I am a chatbot. Send me a message and I will respond.")

def handle_command(command, chat_id):
    if command == "/start":
        handle_start(chat_id)
    # Add more command handlers here if needed

def main():
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            if offset:
                url += f"?offset={offset}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad response status codes
            messages = response.json()["result"]
            for message in messages:
                offset = message["update_id"] + 1
                chat_id = message["message"]["chat"]["id"]
                if "text" in message["message"]:
                    user_message = message["message"]["text"]
                    if user_message.startswith("/"):
                        handle_command(user_message, chat_id)
                    else:
                        bot_response = process_message(user_message)
                        send_message(chat_id, bot_response)
            time.sleep(1)  # Avoid excessive polling
        except requests.exceptions.RequestException as e:
            print(f"Error fetching updates: {e}")
            time.sleep(10)  # Wait before retrying

if __name__ == "__main__":
    main()
