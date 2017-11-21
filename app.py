import os, sys, requests, json
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "<FACEBOOK ACCESS TOKEN"
OD_API = "<OXFORD DICTIONARY API>"
APP_ID = "<ID>"
APP_KEY = "<API KEY>"


@app.route('/', methods=['GET'])
def verify():
    ''' Webhook verification, echo back the 'hub.challenge' value it receives
        in the query arguments '''
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # Parse json
    if data["object"] == "page":
        for entry in data['entry']:
            for messaging in entry["messaging"]:
                if messaging.get("message"):
                    # Get the Facebook sender ID
                    sender_id = messaging["sender"]["id"]
                    # Get the Facebook recipient ID
                    recipient_id = messaging["sender"]["id"]
                    # Get the message text
                    message_text = messaging["message"]["text"]
                    message_response = message_result(message_text)
                    # Send a response back
                    send_message(sender_id, message_response)

    return "ok", 200


def extract_result(response, word):
    result = word

    for senses in response["results"][0]["lexicalEntries"][0]["entries"][0]["senses"]:
        if "definitions" not in senses:
            return "Word not found."
        for definition in senses["definitions"]:
            result += "\nDefinition:\n" + definition + "\n"

    return result


def message_result(word_id):
    language = 'en'

    url = OD_API + '/entries/' + language + '/' + word_id.lower()

    r = requests.get(url, headers = {'app_id': APP_ID, 'app_key': APP_KEY})

    if r.status_code == requests.codes.ok:
        return extract_result(r.json(), word_id)
    else:
        return "Word not found."


def send_message(recipient_id, message_text):
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    # To json string, requires messaging_type, recipient, and message
    data = json.dumps({
        "message_type": "RESPONSE",
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    # Request URI
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)


if __name__ == "__main__":
    app.run(debug = True, port = 5000)
