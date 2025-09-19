# handlers/sites.py - Команды Telegram
from aiogram import Router, F,types
from aiogram.types import Message
from database import SessionLocal
from models import Site, SiteHistory
from datetime import datetime, timedelta
import validators
import csv
import io
import logging

router = Router()
logging.basicConfig(filename='bot.log', level=logging.INFO)

@router.message(F.text == "/start")
async def start_command(message: Message):
    commands = (
        "👋 Привет! Я бот для мониторинга сайтов.\n\n"
        "📌 Доступные команды:\n"
        "• /addsite <url> — добавить новый сайт\n"
        "   Например: /addsite https://google.com\n"
        "• /listsites — список сайтов\n"
        "• /delsite <id> — удалить сайт\n"
        "   Например: /delsite 1\n"
        "• /setinterval <id> <минуты> — задать интервал проверки\n"
        "   Например: /setinterval 1 10\n"
        "• /toggle_notifications <id> — переключить уведомления\n"
        "   Например: /toggle_notifications 1\n"
        "• /history <id> — история последних проверок\n"
        "   Например: /history 1\n"
        "• /uptime <id> — статистика доступности за 24 часа\n"
        "   Например: /uptime 1\n"
        "• /export <id> — экспорт истории в CSV\n"
        "   Например: /export 1\n"
    )
    await message.answer(commands)

@router.message(F.text.regexp(r"^/addsite(\s|$)"))
async def add_site(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❗ Использование: /addsite https://example.com")
        return

    url = parts[1].strip()

    if not validators.url(url):
        await message.answer("❌ Введен неверный URL!")
        return

    db = SessionLocal()
    existing = db.query(Site).filter(Site.url == url).first()
    if existing:
        await message.answer("⚠️ Этот сайт уже добавлен.", disable_web_page_preview=True)
    else:
        new_site = Site(url=url)
        db.add(new_site)
        db.commit()
        await message.answer(f"✅ Сайт добавлен: {url}", disable_web_page_preview=True)
    db.close()

@router.message(F.text.regexp(r"^/listsites(\s|$)"))
async def list_sites(message: Message):
    db = SessionLocal()
    sites = db.query(Site).all()
    if not sites:
        await message.answer("Список сайтов пуст.", disable_web_page_preview=True)
    else:
        text = "\n".join([f"{s.id}. {s.url} ({s.interval} мин, Уведомления: {'Включены' if s.notifications_enabled else 'Выключены'})" for s in sites])
        await message.answer("📋 Сайты:\n" + text, disable_web_page_preview=True)
    db.close()

@router.message(F.text.regexp(r"^/delsite(\s|$)"))
async def delete_site(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❗ Использование: /delsite site_id")
        return

    try:
        site_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    db = SessionLocal()
    site = db.query(Site).filter(Site.id == site_id).first()
    if site:
        db.delete(site)
        db.commit()
        await message.answer(f"🗑️ Сайт удален: {site.url}")
    else:
        await message.answer("⚠️ Такой ID не найден.")
    db.close()

@router.message(F.text.regexp(r"^/setinterval(\s|$)"))
async def set_interval(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❗ Использование: /setinterval site_id минуты")
        return

    try:
        site_id = int(parts[1])
        interval = int(parts[2])
    except ValueError:
        await message.answer("❌ ID и интервал должны быть целыми числами!")
        return

    db = SessionLocal()
    site = db.query(Site).filter(Site.id == site_id).first()
    if site:
        site.interval = interval
        db.commit()
        await message.answer(f"⏱️ Интервал для {site.url} установлен на {interval} минут.")
    else:
        await message.answer("⚠️ Такой ID не найден.")
    db.close()

@router.message(F.text.regexp(r"^/toggle_notifications(\s|$)"))
async def toggle_notifications(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❗ Использование: /toggle_notifications site_id")
        return

    try:
        site_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    db = SessionLocal()
    site = db.query(Site).filter(Site.id == site_id).first()
    if site:
        site.notifications_enabled = not site.notifications_enabled
        status = "включены" if site.notifications_enabled else "выключены"
        db.commit()
        await message.answer(f"🔔 Уведомления для {site.url} {status}.")
    else:
        await message.answer("⚠️ Такой ID не найден.")
    db.close()

@router.message(F.text.regexp(r"^/history(\s|$)"))
async def history(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❗ Использование: /history site_id")
        return

    try:
        site_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    db = SessionLocal()
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        await message.answer("⚠️ Такой ID не найден.")
        db.close()
        return

    checks = (
        db.query(SiteHistory)
        .filter(SiteHistory.site_id == site_id)
        .order_by(SiteHistory.checked_at.desc())
        .limit(10)
        .all()
    )
    db.close()

    if not checks:
        await message.answer("ℹ️ Для этого сайта пока нет истории.")
        return

    text = f"📊 История {site.url}:\n\n"
    for c in checks:
        status_icon = "✅" if c.status_code == 200 else "❌"
        checked_time = c.checked_at.strftime("%Y-%m-%d %H:%M:%S")
        text += f"{status_icon} {c.status_code or '-'} | {c.response_time or '-'} мс | {checked_time}\n"

    await message.answer(text)

@router.message(F.text.regexp(r"^/uptime(\s|$)"))
async def uptime(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❗ Использование: /uptime site_id")
        return

    try:
        site_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    db = SessionLocal()
    try:
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            await message.answer("⚠️ Такой ID не найден.")
            return

        since = datetime.utcnow() - timedelta(hours=24)
        checks = (
            db.query(SiteHistory)
            .filter(SiteHistory.site_id == site_id, SiteHistory.checked_at >= since)
            .all()
        )

    except Exception as e:
        logging.error(f"Ошибка uptime: {e}")
        await message.answer(f"⚠️ Ошибка получения данных: {e}")
        return
    finally:
        db.close()

    if not checks:
        await message.answer("ℹ️ Нет данных за последние 24 часа.")
        return

    total = len(checks)
    ok = sum(1 for c in checks if c.status_code == 200)
    uptime_percent = round(ok / total * 100, 2)

    # Группируем проверки по часам
    hours = 24
    uptime_data = [0] * hours
    checks_per_hour = [0] * hours

    now = datetime.utcnow()
    for c in checks:
        hour_index = int((now - c.checked_at).total_seconds() // 3600)
        if 0 <= hour_index < hours:
            checks_per_hour[hour_index] += 1
            if c.status_code == 200:
                uptime_data[hour_index] += 1

    # ASCII график
    graph_lines = []
    for h in range(hours):
        if checks_per_hour[h] > 0:
            hour_uptime = uptime_data[h] / checks_per_hour[h] * 100
            bars = "█" * int(hour_uptime / 10)  # 10% = 1 блок
            graph_lines.append(f"{h:02d}h: {bars or '░'} ({hour_uptime:.0f}%)")
        else:
            graph_lines.append(f"{h:02d}h: ─ (нет данных)")

    graph = "\n".join(graph_lines)

    text = (
        f"📈 <b>Uptime для {site.url} (24ч):</b>\n\n"
        f"🔢 Проверок: {total}\n"
        f"✅ Uptime: {uptime_percent}%\n\n"
        f"📊 График по часам:\n{graph}"
    )

    await message.answer(text, parse_mode="HTML")

@router.message(F.text.regexp(r"^/export(\s|$)"))
async def export_history(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❗ Использование: /export site_id")
        return

    try:
        site_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Неверный ID!")
        return

    db = SessionLocal()
    try:
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            await message.answer("⚠️ Такой ID не найден.")
            return

        checks = db.query(SiteHistory).filter(SiteHistory.site_id == site_id).all()
        if not checks:
            await message.answer("ℹ️ История отсутствует.")
            return

        # Создание CSV файла
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Статус', 'Время ответа (мс)', 'Дата проверки', 'Хэш контента'])
        for c in checks:
            writer.writerow([c.id, c.status_code, c.response_time, c.checked_at, c.content_hash])

        csv_content = output.getvalue()
        output.close()

        # Файлнейм без спецсимволов
        safe_name = site.url.replace("https://", "").replace("http://", "").replace("/", "_")
        filename = f"{safe_name}_history.csv"

        await message.answer_document(
            document=types.BufferedInputFile(csv_content.encode('utf-8'), filename=filename),
            caption=f"📄 История {site.url} экспортирована."
        )

    except Exception as e:
        logging.error(f"Ошибка экспорта CSV: {e}")
        await message.answer(f"⚠️ Ошибка экспорта: {e}")
    finally:
        db.close()