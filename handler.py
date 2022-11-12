import json


def receive(event, context):
    """
    Receive callback to URL when message is sent in the group.
    """
    # Retrieve data on that single GroupMe message.
    message = json.loads(event['body'])
    bot_id = message['bot_id']
    reply(message, group_id)

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


# Webhook receipt and response
def receive():


def reply(message, group_id):
    response = ingest(message)
    if response:
        send(response, group_id)


def ingest(message):
    response = None
    text = message["text"].strip()
    if message["sender_type"] == "user" and text.startswith(PREFIX):
        if message["text"].endswith(SUFFIX):
            img = BytesIO()
            imagesize = "bbox"
            offset = "0.3cm,0.3cm"
            resolution = 400
            backcolor = "White"
            forecolor = "Black"
            dvi = r"-T %s -D %d -bg %s -fg %s -O %s" % (imagesize,
                                                        resolution,
                                                        backcolor,
                                                        forecolor,
                                                        offset)
            dvioptions = dvi.split()
            try:
                sympy.preview(text, output="png", viewer="BytesIO",
                              outputbuffer=img, euler=False, dvioptions=dvioptions)
                url = upload_image(img.getvalue())
                response = ("", url)
            except Exception as e:
                print(e)
                response = ("There was an error typsesetting the equation you specified. Please check your syntax, or report a bug at https://github.com/ErikBoesen/texbot/issues/new!", "")
        else:
            command = text.lower().lstrip(PREFIX).split()[0]
            if command == "info":
                return ("I'm TeXbot, a helpful tool that you can use to typeset (La)TeX math in GroupMe! I was made by Erik Boesen (erikboesen.com). You can see more information and add me to your own chat at https://mebots.co/bot/texbot. My source code is at https://github.com/ErikBoesen/texbot.", "")
    return response


def send(message: tuple, group_id):
    """
    Reply in chat.
    :param message: Tuple of message text and picture URL.
    :param group_id: ID of group in which to send message.
    """
    text, picture_url = message
    # Prevent us from trying to send nothing
    if text or picture_url:
        text = text or ""
        picture_url = picture_url or ""
        payload = {
            "bot_id": bot.instance(group_id).id,
            "text": text,
            "picture_url": picture_url,
        }
        response = requests.post("https://api.groupme.com/v3/bots/post", json=payload)


