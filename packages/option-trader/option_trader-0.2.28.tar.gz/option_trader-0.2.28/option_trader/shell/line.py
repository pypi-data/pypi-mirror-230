from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser

import random

app = Flask(__name__)

LINE_CHANNEL_SECRET = '628e7b113c8927a8a81e6e5f34412ffe'
LINE_USER_ID = '628e7b113c8927a8a81e6e5f34412ffe'
LINE_BOT_BASIC_ID = '@713hvlic'
LINE_CHANNEL_ACCESS_TOKEN = 'eNyfeZLsU7MbVSU8oWu+iryZ6yzVuO575vB71iNtjBbbNznkoPfsTbxhz+hbHX1m745hV/Zm90r4/fsUFTKeB9I5axHBQC4jRPMqAxniBO2wkVzdNs9X28czaoKixH1lxaefvcLEtFkZMqy2qNs8vwdB04t89/1O/w1cDnyilFU='


# LINE 聊天機器人的基本資料
#config = configparser.ConfigParser()
#config.read('config.ini')


#line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
#handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

#https://ithelp.ithome.com.tw/articles/10229943

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        # Phoebe 愛唱歌
        pretty_note = '♫♪♬'
        pretty_text = ''
        
        for i in event.message.text:
        
            pretty_text += i
            pretty_text += random.choice(pretty_note)
    
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=pretty_text)
        )

if __name__ == "__main__":
    app.run()