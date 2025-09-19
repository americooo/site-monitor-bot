# reports.py - Еженедельные отчеты
from database import SessionLocal
from models import Site, SiteHistory
from aiogram import Bot
from datetime import datetime, timedelta
import asyncio
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO)

async def send_weekly_report(bot: Bot, admin_id):
    while True:
        try:
            db = SessionLocal()
            sites = db.query(Site).all()
            report = "<b>Еженедельный Отчет</b>\n\n"
            week_ago = datetime.utcnow() - timedelta(days=7)

            for site in sites:
                history = db.query(SiteHistory).filter(
                    SiteHistory.site_id == site.id,
                    SiteHistory.checked_at >= week_ago
                ).all()
                if not history:
                    continue

                total = len(history)
                up = sum(1 for h in history if h.status_code == 200)
                down = total - up
                avg_response = sum(h.response_time for h in history) / total if total > 0 else 0

                report += (
                    f"{site.url}\n"
                    f"✅ {up / total * 100:.1f}% доступен\n"
                    f"❌ {down / total * 100:.1f}% недоступен\n"
                    f"⏱ {avg_response:.0f} мс среднее\n\n"
                )

            db.close()
            if len(report) > 50:  # Если отчет не пустой
                await bot.send_message(admin_id, report, parse_mode="HTML")
            await asyncio.sleep(7 * 24 * 60 * 60)  # 1 неделя

        except Exception as e:
            logging.error(f"Ошибка задачи еженедельного отчета: {e}")
            print("Ошибка задачи еженедельного отчета:", e)
            await asyncio.sleep(5)