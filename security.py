import secrets

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()

REAL_API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Security(api_key_header)):
    # secrets.compare_digest порівнює рядки за фіксований час, незалежно від того,
    # на якому символі вони розійшлися. Звичайне "!=" виходить одразу при першій
    # незбіжності, тому час відповіді теоретично видає, скільки символів ключа
    # вгадано правильно (timing attack). compare_digest закриває цю дірку.
    if not REAL_API_KEY or not secrets.compare_digest(key, REAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return key