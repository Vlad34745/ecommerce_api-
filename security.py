import os
import secrets

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

load_dotenv()

REAL_API_KEY = os.getenv("API_KEY")

if not REAL_API_KEY:  # pragma: no cover - exercised only when .env is missing/misconfigured
    # Без цієї перевірки verify_api_key просто відхиляв би БУДЬ-який ключ (навіть
    # правильний) з незрозумілою причини — виглядало б як "API зламане", хоча
    # насправді забули задати змінну середовища.
    raise RuntimeError(
        "API_KEY is not set. Create a .env file based on .env.example "
        "(see the 'How to Run Locally' section in README.md)."
    )

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Security(api_key_header)):
    # secrets.compare_digest порівнює рядки за фіксований час, незалежно від того,
    # на якому символі вони розійшлися. Звичайне "!=" виходить одразу при першій
    # незбіжності, тому час відповіді теоретично видає, скільки символів ключа
    # вгадано правильно (timing attack). compare_digest закриває цю дірку.
    if not secrets.compare_digest(key, REAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return key