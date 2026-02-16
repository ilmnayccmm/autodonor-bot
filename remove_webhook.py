import asyncio
from aiogram import Bot

API_TOKEN = "8559331716:AAEbQ7X0LmBw0pQukl9Y0EZAj2qg0ywLlpE"

async def main():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook()  # видаляє старий webhook
    print("Webhook видалено ✅")
    await bot.session.close()

asyncio.run(main())
