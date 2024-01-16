import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
import os
import openai

load_dotenv()
# токен бота
TOKEN = os.getenv('TG_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')

openai.api_key = OPENAI_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    # Отправляем приветственное сообщение
    await update.message.reply_text("Привет! Как я могу помочь тебе сегодня?")

async def get_openai_response(context: CallbackContext, user_id, message):
    if 'chat_sessions' not in context.bot_data:
        context.bot_data['chat_sessions'] = {}

    session = context.bot_data['chat_sessions'].get(user_id, {'messages': []})

    # Добавляем сообщение пользователя в сессию
    session['messages'].append({'role': 'user', 'content': message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=session['messages']
    )

    # Добавляем ответ модели в сессию для сохранения контекста
    session['messages'].append(response['choices'][0]['message'])

    # Сохраняем обновленную сессию
    context.bot_data['chat_sessions'][user_id] = session

    return response['choices'][0]['message']['content']

async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.message.from_user.id

    answer = await get_openai_response(context, user_id, text)
    await update.message.reply_text(answer)

def main():
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    command_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

    application.add_handler(command_handler)
    application.add_handler(message_handler)

    application.run_polling()
    print('Бот остановлен')

if __name__ == '__main__':
    main()
