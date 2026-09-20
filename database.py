import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:  # pragma: no cover - exercised only when .env is missing/misconfigured
    # Без цієї перевірки create_engine(None) впав би з незрозумілою помилкою
    # SQLAlchemy десь у надрах бібліотеки. Так — одразу зрозуміло, що робити.
    raise RuntimeError(
        "DATABASE_URL is not set. Create a .env file based on .env.example "
        "(see the 'How to Run Locally' section in README.md)."
    )

IS_SQLITE = DATABASE_URL.startswith("sqlite")

# SQLite за замовчуванням дозволяє використовувати з'єднання лише в тому потоці,
# де воно було створене. FastAPI/pytest можуть звертатися до сесії з іншого
# потоку, тому для SQLite (яку ми використовуємо в тестах — див. tests/conftest.py)
# вимикаємо цю перевірку через check_same_thread=False. На робочу базу
# (Postgres) це ніяк не впливає — connect_args лишається порожнім.
connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

if IS_SQLITE:
    # На відміну від Postgres, SQLite за замовчуванням НЕ перевіряє foreign key
    # constraints, доки їх явно не увімкнути через PRAGMA. Без цього рядка тести
    # на SQLite не помітили б, якби перевірка "не можна видалити товар, поки на
    # нього є замовлення" (delete_product у main.py) десь зламалась — вона просто
    # мовчки не спрацьовувала б у тестовому середовищі, хоч на Postgres працює.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():  # pragma: no cover - overridden in tests by conftest.py
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()