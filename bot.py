import os
import telebot
import requests

BOT_TOKEN = "8966675976:AAGxJP1V6f-SE7htoUQrLmYylxxW78vpqc8"
MARKET_API_KEY = "idKSeCHgGxKs2mDBU7HGPKHDDyUxnzIP6S"
API_BASE_URL = "https://id.majestic-rp.ru/api"

bot = telebot.TeleBot(BOT_TOKEN)

def get_market_data(endpoint, params=None):
    if params is None:
        params = {}
    headers = {
        "Authorization": f"Bearer {MARKET_API_KEY}",
        "X-API-Key": MARKET_API_KEY,
        "User-Agent": "MajesticMarketBot/1.0"
    }
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Ошибка API: {e}")
    return None

def main_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("🚗 Автомобили", callback_data="cat_cars"),
        telebot.types.InlineKeyboardButton("📦 Предметы", callback_data="cat_items")
    )
    markup.row(telebot.types.InlineKeyboardButton("👤 Профиль API", callback_data="check_status"))
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "👋 **Добро пожаловать в Маркетплейс Бот (Majestic / Россия Онлайн)!**",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data == "check_status":
            bot.answer_callback_query(call.id, "Проверка API...")
            data = get_market_data("/me")
            if data:
                bot.edit_message_text("✅ **Статус API:** Подключено!", call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")
            else:
                bot.edit_message_text("⚠️ Ошибка соединения с API.", call.message.chat.id, call.message.message_id, reply_markup=main_keyboard())

        elif call.data.startswith("cat_"):
            cat = call.data.split("_")[1]
            bot.answer_callback_query(call.id, "Загрузка...")
            data = get_market_data("/marketplace/items", params={"category": cat})

            if not data or not data.get("items"):
                bot.edit_message_text("❌ Лоты не найдены.", call.message.chat.id, call.message.message_id, reply_markup=main_keyboard())
            else:
                text = f"📦 **Лоты в категории {cat}:**\n\n"
                for item in data.get("items", [])[:5]:
                    text += f"• **{item.get('title', 'Товар')}** — {item.get('price', 0)} $\n"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")
    except Exception as e:
        print(f"Игнорируем ошибку модификации сообщения: {e}")

if __name__ == '__main__':
    print("Бот запущен на Render!")
    bot.infinity_polling()
