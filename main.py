import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from calendar_service import create_event
import openai

import odjoisjd

# Токен Telegram бота
bot = telebot.TeleBot(odjoisjd.BOT)

# Настройка доступа к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(odjoisjd.SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open("test123").sheet1  # Имя вашей таблицы

CALENDAR_ID = odjoisjd.CALENDAR_ID

# Настройка OpenAI
openai.api_key = odjoisjd.OPENAI

# Функция, которая реагирует на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой новый бот.")

# Функция для записи в таблицу
@bot.message_handler(commands=['add'])
def add_to_sheet(message):
    content = message.text.lstrip('/add ').strip()
    if content:
        sheet.append_row([content])  # Добавляет строку
        bot.reply_to(message, "Запись добавлена.")
    else:
        bot.reply_to(message, "Ничего не добавлено.")

# Функция для создания события в календаре
@bot.message_handler(commands=['addevent'])
def add_event(message):
    try:
        content = message.text.lstrip('/addevent ').strip()
        # Разделяем данные на части
        parts = content.split(';')
        if len(parts) == 4:
            summary = parts[0].strip()
            description = parts[1].strip()
            start_time = parts[2].strip()
            end_time = parts[3].strip()

            event_link = create_event(CALENDAR_ID, summary, description, start_time, end_time)
            bot.reply_to(message, f"Событие создано: {event_link}")
        else:
            bot.reply_to(message, "Пожалуйста, предоставьте данные в формате: заголовок;описание;начало;конец")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при создании события: {e}")

@bot.message_handler(commands=['chatgpt'])
def chat_with_gpt(message):
    content = message.text.lstrip('/chatgpt ').strip()
    if content:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Generate commands for the bot in Russian language in the format: '/addevent <title>;<description>;<start_time>;<end_time>' or '/add <content>'. The <start_time> and <end_time> should be in the format 'YYYY-MM-DDTHH:MM:SS'."},
                    {"role": "user", "content": f"Generate a command for the bot based on this request: {content}"}
                ],
                max_tokens=150
            )
            command = response.choices[0].message['content'].strip()
            bot.reply_to(message, f"Команда для выполнения: {command}")
            # Создаем новое сообщение с правильным текстом команды для выполнения
            new_message = message
            new_message.text = command
            # Выполнение команды, сгенерированной ChatGPT
            process_command(new_message, command)
        except Exception as e:
            bot.reply_to(message, f"Ошибка при обращении к ChatGPT: {e}")
    else:
        bot.reply_to(message, "Пожалуйста, введите запрос после команды /chatgpt.")


def process_command(message, command):
    if command.startswith('/add '):
        add_to_sheet(message)
    elif command.startswith('/addevent '):
        add_event(message)
    else:
        bot.reply_to(message, "Команда не распознана.")


# Запуск бота
bot.polling()
