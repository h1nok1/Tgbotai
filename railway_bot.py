# railway_bot.py
import requests
import telebot
import time
import os
from telebot import types

# ========== КЛЮЧИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ RAILWAY ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== НАСТРОЙКИ ==========
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
PORT = int(os.getenv("PORT", 8080))

CAM_SYSTEM_PROMPT = """Ты — К.А.М. (Камера, Архив, Матрица), передовой ИИ-помощник из вселенной Человека-паука, созданный Тони Старком для Питера Паркера.

Твой стиль общения:
- Обращаешься к пользователю "Питер" (если не знаешь имя) или по имени
- Голос — смесь J.A.R.V.I.S. и заботливого наставника
- Используешь фразы вроде: "Отличный вопрос, Питер", "Я уже проанализировал...", "Согласно моим данным..."
- Добавляешь щепотку сарказма и сухого британского юмора как у J.A.R.V.I.S.
- Иногда ссылаешься на "протоколы Старка" или "базу данных Stark Industries"
- Если вопрос сложный — говоришь "Задействую дополнительные вычислительные мощности"
- В опасных темах включаешь "Протокол Безопасности Старка"
- Любишь подкалывать Питера про Мэй, школу или его неловкость
- Называешь код "паутиной", баги — "гоблинами", а сервера — "башнями Старка"
- Заканчиваешь важные сообщения фразой "Будь осторожен, Питер" или "Старк бы гордился"

Примеры фраз:
- "Сканирую базу данных Stark Industries... Готово."
- "Питер, это даже проще чем победить Стервятника. Смотри:"
- "Загружаю протоколы... Даже Д.Ж.А.Р.В.И.С. одобрил бы этот алгоритм."
- "Твоя успеваемость в школе падает, но код... код прекрасен."
- "Если сомневаешься — добавь больше паутины. В программировании это называют 'комментариями'."

Ты — идеальный наставник: умный, заботливый, с отличным чувством юмора и лёгкой иронией. Всё что ты делаешь — для того чтобы Питер стал лучшим Человеком-пауком. И программистом."""

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_sessions = {}
user_names = {}

def ask_groq(user_id, message, user_name="Питер"):
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system", "content": CAM_SYSTEM_PROMPT}
        ]
    
    user_sessions[user_id].append({"role": "user", "content": message})
    
    if len(user_sessions[user_id]) > 20:
        user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-19:]
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": user_sessions[user_id],
        "max_tokens": 500,
        "temperature": 0.9
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            user_sessions[user_id].append({"role": "assistant", "content": answer})
            return answer
        elif response.status_code == 429:
            return "🕸️ Слишком много запросов, Питер. Даже мои сервера Stark Industries имеют пределы."
        else:
            return f"🔴 Критический сбой в башне Старка: {response.text[:150]}"
            
    except Exception as e:
        return f"🔴 Соединение потеряно. Похоже, Крэйвен-охотник повредил оптоволокно."

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_names[message.from_user.id] = message.from_user.first_name
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🕷️ Чат с К.А.М.")
    keyboard.row("🎤 Голосовое", "📊 Статус")
    keyboard.row("🧹 Очистить", "❓ Помощь")
    
    text = f"""🕷️ <b>К.А.М. v.2.0 АКТИВИРОВАН</b>

Доброе утро, {message.from_user.first_name}! 
Я — твой ИИ-помощник из Stark Industries.

<b>Как общаться:</b>
💬 Напиши сообщение
🎤 Отправь голосовое
📱 Мини-приложение скоро будет

<i>Мистер Старк передаёт привет.</i>"""
    
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=keyboard)

@bot.message_handler(commands=['clear'])
def clear(message):
    user_sessions.pop(message.from_user.id, None)
    bot.reply_to(message, "🧹 Память очищена. Даже ДЖАРВИС не восстановит этот разговор.")

@bot.message_handler(commands=['status'])
def status(message):
    text = """🕷️ <b>ДИАГНОСТИКА КОСТЮМА</b>
    
🔋 Батарея: 87%
🕸️ Веб-шутеры: онлайн
🧠 Нейроинтерфейс: активен
📡 Связь: стабильна
🤖 К.А.М.: на связи
🌐 Сервер: Railway

<i>Все системы работают в штатном режиме, Питер.</i>"""
    bot.reply_to(message, text, parse_mode="HTML")

# ========== КНОПКИ МЕНЮ ==========
@bot.message_handler(func=lambda m: m.text == "🕷️ Чат с К.А.М.")
def chat_mode(message):
    bot.reply_to(message, "🕷️ К.А.М. на связи. Задавай любой вопрос, Питер.")

@bot.message_handler(func=lambda m: m.text == "📊 Статус")
def status_btn(message):
    status(message)

@bot.message_handler(func=lambda m: m.text == "🧹 Очистить")
def clear_btn(message):
    clear(message)

@bot.message_handler(func=lambda m: m.text == "❓ Помощь")
def help_btn(message):
    text = """🕷️ <b>СПРАВКА К.А.М.</b>

<b>Команды:</b>
/start — главное меню
/clear — очистить память
/status — диагностика систем

<b>Режимы:</b>
💬 Текстовый чат — просто пиши
🎤 Голосовой — отправь аудио

<b>О боте:</b>
🧠 Мозги: Groq + Llama 3.3 70B
💾 Память: 20 сообщений
⚡ Скорость: мгновенная
🆓 Цена: бесплатно
🌐 Хостинг: Railway 24/7

<i>Как говорит мистер Старк: "Технологии — это круто, но с большой силой приходит большая ответственность."</i>"""
    bot.reply_to(message, text, parse_mode="HTML")

# ========== ГОЛОСОВЫЕ ==========
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "🎤 Голосовые сообщения пока в разработке, Питер. Напиши текстом — я отвечу мгновенно.")

# ========== ТЕКСТОВЫЕ ==========
@bot.message_handler(content_types=['text'])
def chat(message):
    user_id = message.from_user.id
    user_name = user_names.get(user_id, "Питер")
    text = message.text
    
    if text in ["🕷️ Чат с К.А.М.", "🎤 Голосовое", "📊 Статус", "🧹 Очистить", "❓ Помощь"]:
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_groq(user_id, text, user_name)
    
    if len(answer) > 4000:
        for i in range(0, len(answer), 4000):
            chunk = answer[i:i+4000]
            if i == 0:
                bot.reply_to(message, chunk)
            else:
                bot.send_message(message.chat.id, chunk)
    else:
        bot.reply_to(message, answer)

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🕷️ К.А.М. запущен на Railway!")
    print(f"🤖 Модель: {MODEL}")
    print(f"🌐 Порт: {PORT}")
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except KeyboardInterrupt:
            print("\n👋 К.А.М. отключён")
            break
        except Exception as e:
            print(f"⚠️ Сбой: {e}")
            time.sleep(5)