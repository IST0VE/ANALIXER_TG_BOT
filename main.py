import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from calendar_service import create_event

import odjoisjd

# Токен Telegram бота
bot = telebot.TeleBot(odjoisjd.BOT)

# Настройка доступа к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('superchat.json', scope)
client = gspread.authorize(creds)
sheet = client.open("test123").sheet1  # Имя вашей таблицы

CALENDAR_ID = odjoisjd.CALENDAR_ID

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

# Запуск бота
bot.polling()
