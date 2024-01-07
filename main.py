import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
import os

load_dotenv()
# токен бота
TOKEN = os.getenv('TG_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("English", callback_data='en'),
         InlineKeyboardButton("Русский", callback_data='ru')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose your language:', reply_markup=reply_markup)

async def set_locale(update: Update, context: CallbackContext):
    query =  update.callback_query
    query.answer()
    if query.data == 'en':
        context.user_data['locale'] = 'en'
        text = "You've chosen English."
    elif query.data == 'ru':
        context.user_data['locale'] = 'ru'
        text = "Вы выбрали русский язык."
    await query.edit_message_text(text=text)

async def text_msg(update: Update, context: CallbackContext):
    locale =  context.user_data.get('locale', 'en')
    if locale == 'en':
        text = "We've received a message from you!"
    elif locale == 'ru':
        text = "Текстовое сообщение получено!"
    await update.message.reply_text(text)

async def voice_msg(update: Update, context: CallbackContext):
    locale = context.user_data.get('locale', 'en')
    img_url = "https://i.pinimg.com/736x/f0/48/9c/f0489ceb101a4bb4f8fd6f6f2c9e2762.jpg"
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url)
    if locale == 'en':
        text = "We've received a voice message from you!"
    elif locale == 'ru':
        text = "Голосовое сообщение получено!"
    await update.message.reply_text(text)

async def photo_msg(update: Update, context: CallbackContext):
    locale = context.user_data.get('locale', 'en')
    if locale == 'en':
        text = "Photo saved!"
    elif locale == 'ru':
        text = "Фотография сохранена!"
    await update.message.reply_text(text)
    file = await update.message.photo[-1].get_file()
    # сохраняем изображение на диск
    await file.download_to_drive("photos/image.jpg")

def main():
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(set_locale))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))
    application.add_handler(MessageHandler(filters.VOICE, voice_msg))
    application.add_handler(MessageHandler(filters.PHOTO, photo_msg))

    application.run_polling()
    print('Бот остановлен')

if __name__ == '__main__':
    main()
