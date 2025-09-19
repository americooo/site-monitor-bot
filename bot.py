import asyncio
from aiogram import Bot, Dispatcher
from handlers.sites import router as sites_router
from dotenv import load_dotenv
from monitoring import monitor_sites
from reports import send_weekly_report
from database import init_db
import os
import logging

# Настройки логирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1861209145

if not TOKEN:
    raise ValueError("❌ Токен BOT_TOKEN не найден! Проверьте файл .env.")

async def main():
    # Инициализация базы данных
    try:
        init_db()
        logging.info("✅ База данных успешно создана.")
    except Exception as e:
        logging.error(f"❌ Ошибка инициализации базы данных: {e}")
        print(f"❌ Ошибка инициализации базы данных: {e}")
        raise

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(sites_router)

    asyncio.create_task(monitor_sites(bot, ADMIN_ID))
    asyncio.create_task(send_weekly_report(bot, ADMIN_ID))

    print("✅ Бот запущен...")
    logging.info("✅ Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())