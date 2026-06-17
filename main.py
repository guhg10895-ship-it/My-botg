import os
import telebot
from openai import OpenAI
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot Is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# စနစ်ထဲကနေ Token တွေကို အလိုအလျောက် ဆွဲယူမယ့်အပိုင်း
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

@bot.message_handler(func=lambda message: True)
def chat_with_gpt(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message.text}]
        )
        reply_text = response.choices[0].message.content
        bot.reply_to(message, reply_text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "ခေတ္တအဆင်မပြေဖြစ်နေပါတယ်။ ခဏနေမှ ပြန်မေးပေးပါ။")

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    print("Bot စတင်နေပါပြီ...")
    bot.polling(none_stop=True)
    