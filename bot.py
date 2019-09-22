# Flask
from flask import Flask, request

# Drawing
import sympy

# Other
import argparse
import mebots
from threading import Thread
import requests
import os
from io import BytesIO


app = Flask(__name__)
bot = mebots.Bot("texbot", os.environ.get("BOT_TOKEN"))

PREFIX = "$$"
SUFFIX = "$$"


# Image processing
def upload_image(data) -> str:
    """
    Send image to GroupMe Image API.

    :param data: compressed image data.
    :return: URL of image now hosted on GroupMe server.
    """
    headers = {
        "X-Access-Token": os.environ["GROUPME_ACCESS_TOKEN"],
        "Content-Type": "image/jpeg",
    }
    r = requests.post("https://image.groupme.com/pictures", data=data, headers=headers)
    return r.json()["payload"]["url"]



# Webhook receipt and response
@app.route("/", methods=["POST"])
def receive():
    """
    Receive callback to URL when message is sent in the group.
    """
    # Retrieve data on that single GroupMe message.
    message = request.get_json()
    group_id = message["group_id"]
    # Begin reply process in a new thread.
    # This way, the request won't time out if a response takes too long to generate.
    Thread(target=reply, args=(message, group_id)).start()
    return "ok", 200


def reply(message, group_id):
    response = ingest(message)
    if response:
        send(response, group_id)


def ingest(message):
    response = None
    if message["sender_type"] == "user" and (message["text"].startswith(PREFIX) and message["text"].endswith(SUFFIX)):
        img = BytesIO()
        sympy.preview(message["text"], output="png", viewer="BytesIO", outputbuffer=img, euler=False)
        url = upload_image(img.getvalue())
        response = ("", url)
    return response


def send(message: tuple, group_id):
    """
    Reply in chat.
    :param message: Tuple of message text and picture URL.
    :param group_id: ID of group in which to send message.
    """
    text, picture_url = message
    text = text or ""
    picture_url = picture_url or ""
    data = {
        "bot_id": bot.instance(group_id).id,
        "text": text,
        "picture_url": picture_url,
    }
    response = requests.post("https://api.groupme.com/v3/bots/post", data=data)


# Local testing
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    args = parser.parse_args()
    if args.command:
        print(ingest({"sender_type": "user", "text": args.command}))

print("Launched!")
