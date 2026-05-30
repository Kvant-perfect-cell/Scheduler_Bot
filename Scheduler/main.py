from app.bot.handlers.handler import router
from app.services.notification_worker import notification_worker
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(router)

async def main():
    asyncio.create_task(notification_worker(bot))
    print("Notification worker started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())