# tests/test_bot.py
import pytest
from database import SessionLocal
from models import Site
from sites import add_site

def test_add_site_valid_url():
    db = SessionLocal()
    url = "https://example.com"
    site = Site(url=url)
    db.add(site)
    db.commit()
    assert db.query(Site).filter(Site.url == url).first() is not None
    db.close()

def test_add_site_invalid_url():
    from aiogram.types import Message
    message = Message(text="/addsite invalid_url")
    response = add_site(message)
    assert "Noto‘g‘ri URL" in response

def test_delete_site():
    db = SessionLocal()
    site = Site(url="https://test.com")
    db.add(site)
    db.commit()
    site_id = site.id
    db.delete(db.query(Site).filter(Site.id == site_id).first())
    db.commit()
    assert db.query(Site).filter(Site.id == site_id).first() is None
    db.close()