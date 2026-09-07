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
        # Если текст сообщения не изменился, просто глушим ошибку Telegram
        print(f"Игнорируем дублирующий клик: {e}")
