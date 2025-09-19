# database.py - Настройки и инициализация базы данных
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    try:
        from models import Site, SiteHistory
        Base.metadata.create_all(bind=engine)
        logging.info("✅ Все таблицы созданы: sites и checks.")
        print("✅ Все таблицы созданы: sites и checks.")
    except Exception as e:
        logging.error(f"❌ Ошибка создания базы данных: {e}")
        print(f"❌ Ошибка создания базы данных: {e}")
        raise

if __name__ == "__main__":
    init_db()