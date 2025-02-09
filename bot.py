import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, CHANNEL_ID, WELCOME_MESSAGE, RESPONSE_MESSAGES
from logger import logger

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Переменная для хранения последнего отправленного сообщения
last_response = None
# Флаг для отслеживания первого запуска
is_first_run = True

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Handle the /start command."""
    try:
        user_name = message.from_user.first_name
        welcome_text = WELCOME_MESSAGE.format(user_name=user_name)
        await message.reply(welcome_text)
        logger.info(f"Sent welcome message to user {user_name} (ID: {message.from_user.id})")
    except Exception as e:
        logger.error(f"Error in start_command: {str(e)}")
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message()
async def handle_message(message: types.Message):
    """Handle incoming messages."""
    global last_response, is_first_run

    try:
        # Log incoming message
        logger.info(f"Received message from user {message.from_user.first_name} (ID: {message.from_user.id})")

        # Ignore messages from the channel
        if message.chat.id == CHANNEL_ID:
            logger.debug(f"Ignoring message from channel {CHANNEL_ID}")
            return

        # Get user information
        user = message.from_user
        message_text = message.text

        # Format the message for forwarding
        forward_text = f"{message_text}\n\n {user.first_name}"
        if user.username:
            forward_text += f" (@{user.username})"

        # Forward message to channel
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=forward_text
        )
        logger.info(f"Forwarded message from user {user.first_name} (ID: {user.id}) to channel")

        # Выбор ответа
        if is_first_run:
            # При первом запуске отправляем первое сообщение
            response_message = RESPONSE_MESSAGES[0]
            is_first_run = False  # Сбрасываем флаг первого запуска
        else:
            # Исключаем повторение сообщений подряд
            available_responses = [msg for msg in RESPONSE_MESSAGES if msg != last_response]
            response_message = random.choice(available_responses)

        # Обновляем последнее отправленное сообщение
        last_response = response_message

        # Send response to user
        await message.reply(response_message)
        logger.info(f"Sent response message to user {user.first_name} (ID: {user.id})")

    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        await message.reply("Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте позже.")

async def main():
    """Start the bot."""
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())