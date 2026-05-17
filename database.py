import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no está definida. Crea un archivo .env en la carpeta backend."
    )

connect_args = (
    {"check_same_thread": False}
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_service_gallery_title_column() -> None:
    """Añade service_galleries.title en bases ya creadas (create_all no altera tablas)."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "service_galleries" not in insp.get_table_names():
        return

    columns = {col["name"] for col in insp.get_columns("service_galleries")}
    if "title" in columns:
        return

    dialect = engine.dialect.name
    if dialect == "mysql":
        ddl = "ALTER TABLE service_galleries ADD COLUMN title VARCHAR(255) NULL"
    elif dialect == "sqlite":
        ddl = "ALTER TABLE service_galleries ADD COLUMN title VARCHAR(255)"
    else:
        ddl = "ALTER TABLE service_galleries ADD COLUMN title VARCHAR(255)"

    with engine.begin() as conn:
        conn.execute(text(ddl))


def ensure_services_subtitle_column() -> None:
    """Añade services.subtitle en bases ya creadas."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "services" not in insp.get_table_names():
        return

    columns = {col["name"] for col in insp.get_columns("services")}
    if "subtitle" in columns:
        return

    dialect = engine.dialect.name
    if dialect == "mysql":
        ddl = "ALTER TABLE services ADD COLUMN subtitle VARCHAR(255) NULL"
    elif dialect == "sqlite":
        ddl = "ALTER TABLE services ADD COLUMN subtitle VARCHAR(255)"
    else:
        ddl = "ALTER TABLE services ADD COLUMN subtitle VARCHAR(255)"

    with engine.begin() as conn:
        conn.execute(text(ddl))


def ensure_sliders_active_column() -> None:
    """Añade sliders.active en bases ya creadas."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "sliders" not in insp.get_table_names():
        return

    columns = {col["name"] for col in insp.get_columns("sliders")}
    if "active" in columns:
        return

    dialect = engine.dialect.name
    if dialect == "mysql":
        ddl = "ALTER TABLE sliders ADD COLUMN active TINYINT(1) NOT NULL DEFAULT 1"
    elif dialect == "sqlite":
        ddl = "ALTER TABLE sliders ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1"
    else:
        ddl = "ALTER TABLE sliders ADD COLUMN active BOOLEAN NOT NULL DEFAULT TRUE"

    with engine.begin() as conn:
        conn.execute(text(ddl))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
