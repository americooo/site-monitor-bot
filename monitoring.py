# monitoring.py - Мониторинг сайтов
from database import SessionLocal
from models import Site, SiteHistory
from aiogram import Bot
import asyncio
import time
import aiohttp
import hashlib
from datetime import datetime
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO)

previous_status = {}
previous_content_hash = {}

async def monitor_sites(bot: Bot, admin_id):
    while True:
        try:
            db = SessionLocal()
            sites = db.query(Site).all()

            for site in sites:
                try:
                    start_time = time.time()
                    headers = {"User-Agent": "Mozilla/5.0"}
                    async with aiohttp.ClientSession() as session:
                        async with session.get(site.url, headers=headers, timeout=10) as response:
                            response_time = int((time.time() - start_time) * 1000)
                            status = response.status
                            content = await response.text()
                            content_hash = hashlib.md5(content.encode()).hexdigest()

                            # Сохранение в базу данных
                            entry = SiteHistory(
                                site_id=site.id,
                                status_code=status,
                                response_time=response_time,
                                content_hash=content_hash,
                                checked_at=datetime.utcnow()
                            )
                            db.add(entry)
                            db.commit()

                            # Уведомление об изменении статуса
                            if previous_status.get(site.url) != status:
                                if status == 200:
                                    await bot.send_message(admin_id, f"✅ {site.url} снова работает ({response_time} мс)")
                                else:
                                    await bot.send_message(admin_id, f"❌ {site.url} не работает (статус {status})")

                            # Уведомление об изменении контента
                            if previous_content_hash.get(site.url) and previous_content_hash[site.url] != content_hash:
                                await bot.send_message(admin_id, f"⚠️ Контент {site.url} изменился!")

                            previous_status[site.url] = status
                            previous_content_hash[site.url] = content_hash

                except Exception as e:
                    await bot.send_message(admin_id, f"❌ Ошибка: {site.url}\n{e}")

            db.close()
            await asyncio.sleep(60)  # Проверка каждую минуту

        except Exception as e:
            logging.error(f"Ошибка мониторинга: {e}")
            await asyncio.sleep(5)