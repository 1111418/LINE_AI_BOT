from flask import Flask, request, abort, jsonify

import json

from linebot import(
    LineBotApi, WebhookHandler
) 
from linebot.exceptions import(
    InvalidSignatureError
) 
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    LocationSendMessage, VideoSendMessage, ImageSendMessage,
    StickerSendMessage, LocationMessage,
    VideoMessage, StickerMessage, ImageMessage, Message,
    AudioMessage, FileMessage
)

import google.generativeai as genai

api_key = 'AIzaSyAdQl8-qAm_OlMSCr9hlAfd8xohTzmOpus'
genai.configure(api_key = api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

app = Flask(__name__)

line_bot_api= LineBotApi('9Y/wLGx7LLyFchpTwXZzjL/O8EvpvMULw4mpk3kI13HG+Chjm1yAlgSPrOr7Ax5CGCTkZ9ZcF7PbmqmbVVRDChPRVqPjqaBFVJUMzB5L3NZRRW4BgsDFI0hCEtV6UjZiYLxqZEGHDUANnLwIB3XlzgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6ceef916f89cc4946483ebc06475b487')

history_dict = {}

@app.route('/', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid")
        abort(400)
    
    return 'ok'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text

    if user_text.strip().lower() == "user id":
        print(f"\n***使用者id: {user_id}***\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{user_id}")
        )
        return

    if user_text.strip() in ["幸運小語"]:
        prompt = "請幫我隨機生成一個正面、鼓勵人心的幸運小語。"
        try:
            response = model.generate_content(prompt)
            reply_text = getattr(response, 'text', str(response))
        except Exception as e:
            reply_text = f"發生錯誤: {e}"

        if user_id not in history_dict:
            history_dict[user_id] = []
        history_dict[user_id].append({'user': user_text, 'bot': reply_text})
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return

    try:
        response = model.generate_content(user_text)
        reply_text = getattr(response, 'text', str(response))
    except Exception as e:
        reply_text = f"發生錯誤: {e}"
    # 儲存使用者訊息與bot回覆
    if user_id not in history_dict:
        history_dict[user_id] = []
    history_dict[user_id].append({'user': user_text, 'bot': reply_text})
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(reply_text)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆圖片")
    )
    
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆貼圖")
    )
        
@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆影片")
    )

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆位置")
    )

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆音訊")
    )

@handler.add(MessageEvent, message=FileMessage)
def handle_file(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆檔案")
    )


@handler.add(MessageEvent, message=Message)
def handle_other(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="無法回覆")
    )

@app.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """查詢指定user_id的歷史對話"""
    history = history_dict.get(user_id, [])
    return jsonify(history)

@app.route('/history/<user_id>', methods=['DELETE'])
def delete_history(user_id):
    """刪除指定user_id的歷史對話"""
    if user_id in history_dict:
        del history_dict[user_id]
        return 'Deleted', 200
    else:
        return 'Not found', 404

if __name__ == "__main__":
    app.run()
