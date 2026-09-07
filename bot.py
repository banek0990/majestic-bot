import os
import threading
from flask import Flask
import telebot
from telebot import types

# 1. Легкий веб-сервер для держки Render в статусе Live
app = Flask(__name__)

@app.route('/')
def home():
    return "Majestic Assistant Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Инициализация бота
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8966675976:AAGxJPlV6f-SE7htoUQrLmYylxxW78vpqc8")
bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище заметок в памяти
user_notes = {}

# Главное меню
def main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🧮 Калькулятор Комиссии", callback_data="calc"),
        types.InlineKeyboardButton("📜 Шпора Кодексов", callback_data="codes"),
        types.InlineKeyboardButton("📝 Мои Заметки", callback_data="notes"),
        types.InlineKeyboardButton("ℹ️ О боте", callback_data="info")
    )
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "👋 **Добро пожаловать в Majestic RP Helper!**\n\n"
        "Ваш персональный бот-помощник готов к работе без лишних авторизаций.",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data == "calc":
            msg = bot.send_message(
                call.message.chat.id,
                "📊 **Калькулятор Маркетплейса**\n\n"
                "Введите цену, за которую планируете продать item/авто (только число, например: `150000`):"
            )
            bot.register_next_step_handler(msg, process_calc)

        elif call.data == "codes":
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("🛑 Уголовный Кодекс (УК)", callback_data="code_uk"),
                types.InlineKeyboardButton("📋 Админ. Кодекс (КоАП)", callback_data="code_koap"),
                types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main")
            )
            bot.edit_message_text("Выберите кодекс для быстрого поиска:", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data == "code_uk":
            text = (
                "⚖️ **Краткая шпора УК:**\n\n"
                "• **Статья 10.1** — Умышленное убийство (4 звезды).\n"
                "• **Статья 10.6** — Ограбление / Разбой (3 звезды).\n"
                "• **Статья 12.8** — Незаконное ношение оружия (3 звезды).\n"
                "• **Статья 17.1** — Посягательство на жизнь гос. служащего (5 звёзд).\n"
                "• **Статья 17.6** — Неповиновение законному требованию (2 звезды)."
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")

        elif call.data == "code_koap":
            text = (
                "📋 **Краткая шпора КоАП:**\n\n"
                "• **Статья 3.1** — Превышение скорости (Штраф $500–$1500).\n"
                "• **Статья 3.5** — Парковка в неположенном месте (Штраф + Эвакуация).\n"
                "• **Статья 5.2** — Оскорбление гос. служащего (Штраф $3000)."
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")

        elif call.data == "notes":
            chat_id = call.message.chat.id
            notes = user_notes.get(chat_id, [])
            if not notes:
                text = "📝 **Ваши заметки пусты.**\nНапишите команду `/add Название лота - 50000$`, чтобы сохранить запись!"
            else:
                text = "📝 **Ваши сохраненные записи:**\n\n" + "\n".join([f"• {n}" for n in notes])
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")

        elif call.data == "info":
            bot.edit_message_text("🤖 **Majestic RP Assistant**\nРаботает 24/7 на Render без сбоев.", call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(), parse_mode="Markdown")

        elif call.data == "back_main":
            bot.edit_message_text("Выберите нужную функцию:", call.message.chat.id, call.message.message_id, reply_markup=main_keyboard())

    except Exception as e:
        print(f"Ошибка в бота: {e}")

def process_calc(message):
    try:
        price = float(message.text.replace(" ", ""))
        tax_standard = price * 0.05  # Стандартная комиссия 5%
        tax_vip = price * 0.025     # Скидка с VIP (2.5%)

        profit_std = price - tax_standard
        profit_vip = price - tax_vip

        res = (
            f"💰 **Расчет для цены: {price:,.0f} $**\n\n"
            f"• Без VIP (Комиссия 5%): **{tax_standard:,.0f} $** | Чистыми: **{profit_std:,.0f} $**\n"
            f"• С VIP (Комиссия 2.5%): **{tax_vip:,.0f} $** | Чистыми: **{profit_vip:,.0f} $**"
        )
        bot.send_message(message.chat.id, res, reply_markup=main_keyboard(), parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите корректное число без букв.", reply_markup=main_keyboard())

@bot.message_handler(commands=['add'])
def add_note(message):
    chat_id = message.chat.id
    note_text = message.text.replace("/add", "").strip()
    if note_text:
        if chat_id not in user_notes:
            user_notes[chat_id] = []
        user_notes[chat_id].append(note_text)
        bot.send_message(chat_id, f"✅ Заметка добавлена: *{note_text}*", parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        bot.send_message(chat_id, "⚠️ Укажите текст заметки после команды `/add`", parse_mode="Markdown")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    print("Бот-помощник официально запущен!")
    bot.infinity_polling()
