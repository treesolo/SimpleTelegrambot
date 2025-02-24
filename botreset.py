import asyncio
from aiogram import Bot

TOKEN = "8091694690:AAGQC7WTMQmWC33R7w34WEzdYm_fPyPbq9A"

async def delete_webhook():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook deleted!")
    await bot.close()  # Закрываем сессию бота

# Запуск асинхронной функции
asyncio.run(delete_webhook())