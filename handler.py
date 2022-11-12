import json
import requests
import os
from io import BytesIO


PREFIX = "$"
SUFFIX = "$"


def receive(event, context):
    """
    Receive callback to URL when message is sent in the group.
    """
    # Retrieve data on that single GroupMe message.
    message = json.loads(event["body"])
    bot_id = message["bot_id"]
    token = message["token"]
    reply(message, bot_id, token)

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

# Image processing
def upload_image(data, token) -> str:
    """
    Send image to GroupMe Image API.

    :param data: compressed image data.
    :param token: GroupMe token to use for upload.
    :return: URL of image now hosted on GroupMe server.
    """
    headers = {
        "X-Access-Token": token,
        "Content-Type": "image/jpeg",
    }
    r = requests.post("https://image.groupme.com/pictures", json=data, headers=headers)
    return r.json()["payload"]["url"]


def reply(message, bot_id, token):
    response = ingest(message)
    if response:
        send(response, bot_id)


def ingest(message):
    response = None
    text = message["text"].strip()
    if message["sender_type"] == "user" and text.startswith(PREFIX):
        if message["text"].endswith(SUFFIX):
            data = {
                "formula": message["text"],
                "fsize": "50px",
                "fcolor": "000000",
                "bcolor": "ffffff",
                "errors": "1",
                "preamble": "\\usepackage{amsmath}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}",
            }
            data_text = "&".join([key + "=" + value for key, value in data.items()])

            response = requests.post("https://quicklatex.com/latex3.f", data=data_text)

            lines = response.text.split("\r\n")
            status = int(lines[0])
            if status == 0:
                url = lines[1].split()[0]
                return (url, "")
            else:
                return ("\n".join(lines[2:]), "")
            """
            try:
                sympy.preview(text, output="png", viewer="BytesIO",
                              outputbuffer=img, euler=False, dvioptions=dvioptions)
                url = upload_image(img.getvalue())
                response = ("", url)
            except Exception as e:
                print(e)
                response = ("There was an error typsesetting the equation you specified. Please check your syntax, or report a bug at https://github.com/ErikBoesen/texbot/issues/new!", "")
            """
        else:
            command = text.lower().lstrip(PREFIX).split()[0]
            if command == "info":
                return ("I'm TeXbot, a helpful tool that you can use to typeset (La)TeX math in GroupMe! You can see more information and add me to your own chat at https://mebots.io/bot/texbot. My source code is at https://github.com/ErikBoesen/texbot.", "")
    return response


def send(message: tuple, bot_id):
    """
    Reply in chat.
    :param message: Tuple of message text and picture URL.
    :param id_id: ID of bot instance to use for sending message.
    """
    text, picture_url = message
    # Prevent us from trying to send nothing
    if text or picture_url:
        text = text or ""
        picture_url = picture_url or ""
        payload = {
            "bot_id": bot_id,
            "text": text,
            "picture_url": picture_url,
        }
        response = requests.post("https://api.groupme.com/v3/bots/post", json=payload)
