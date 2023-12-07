from flask import Flask, request, abort  
from linebot import LineBotApi, WebhookHandler  
from linebot.exceptions import InvalidSignatureError  
from linebot.models import MessageEvent, TextMessage, TextSendMessage  
from api.chatgpt import ChatGPT  
import os  
import csv

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))  
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))  
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"  

app = Flask(__name__)  
chatgpt = ChatGPT()

# Load keyword-response pairs
keyword_response_dict = {}
with open('EAP相關網站.csv', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        keyword_response_dict[row[0]] = row[1]

@app.route('/')  
def home():  
    return 'Hello, World!'  

@app.route("/webhook", methods=['POST'])  
def callback():  
    # get X-Line-Signature header value  
    signature = request.headers['X-Line-Signature']  
    # get request body as text  
    body = request.get_data(as_text=True)  
    app.logger.info("Request body: " + body)  
    # handle webhook body  
    try:  
        line_handler.handle(body, signature)  
    except InvalidSignatureError:  
        abort(400)  
    return 'OK'  

@line_handler.add(MessageEvent, message=TextMessage)  
def handle_message(event):  
    global working_status  
    if event.message.type != "text":  
        return  

    text = event.message.text  

    for keyword in keyword_response_dict.keys():
        if keyword in text:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=keyword_response_dict[keyword]))
            return

    if text == "說話":  
        working_status = True  
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="我可以說話囉，歡迎來跟我互動 ^_^ "))  
        return  

    if text == "閉嘴":  
        working_status = False  
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我繼續說話，請跟我說 「說話」 > <"))  
        return  

    if working_status:  
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")  
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)  
        chatgpt.add_msg(f"AI:{reply_msg}\n")  
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))  

if __name__ == "__main__":  
    app.run
