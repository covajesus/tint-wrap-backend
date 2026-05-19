import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Siempre backend/.env (misma carpeta que este archivo)
_ENV_FILE = Path(__file__).resolve().parent / ".env"
if not _ENV_FILE.is_file():
    raise RuntimeError(f"No se encontró el archivo {_ENV_FILE}")

load_dotenv(_ENV_FILE)


def _env(key: str) -> str | None:
    value = os.getenv(key)
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


SQLALCHEMY_DATABASE_URL = _env("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL no está definida en {_ENV_FILE}"
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


def ensure_users_table() -> None:
    """Renombra admin_users → users en bases creadas antes del cambio de nombre."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    tables = set(insp.get_table_names())
    if "users" in tables:
        return
    if "admin_users" not in tables:
        return

    dialect = engine.dialect.name
    with engine.begin() as conn:
        if dialect == "mysql":
            conn.execute(text("RENAME TABLE admin_users TO users"))
        elif dialect == "sqlite":
            conn.execute(text("ALTER TABLE admin_users RENAME TO users"))
        else:
            conn.execute(text("ALTER TABLE admin_users RENAME TO users"))


def ensure_users_password_column() -> None:
    """Renombra users.password_hash → password en bases ya creadas."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return

    columns = {col["name"] for col in insp.get_columns("users")}
    if "password" in columns:
        return
    if "password_hash" not in columns:
        return

    dialect = engine.dialect.name
    if dialect == "mysql":
        ddl = "ALTER TABLE users CHANGE COLUMN password_hash password VARCHAR(255) NOT NULL"
    else:
        ddl = "ALTER TABLE users RENAME COLUMN password_hash TO password"

    with engine.begin() as conn:
        conn.execute(text(ddl))


def ensure_blogs_date_columns() -> None:
    """Añade blogs.added_date y blogs.updated_date en bases ya creadas."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "blogs" not in insp.get_table_names():
        return

    columns = {col["name"] for col in insp.get_columns("blogs")}
    dialect = engine.dialect.name

    with engine.begin() as conn:
        if "added_date" not in columns:
            if dialect == "mysql":
                conn.execute(
                    text("ALTER TABLE blogs ADD COLUMN added_date DATETIME NULL")
                )
            else:
                conn.execute(text("ALTER TABLE blogs ADD COLUMN added_date DATETIME"))

        if "updated_date" not in columns:
            if dialect == "mysql":
                conn.execute(
                    text("ALTER TABLE blogs ADD COLUMN updated_date DATETIME NULL")
                )
            else:
                conn.execute(text("ALTER TABLE blogs ADD COLUMN updated_date DATETIME"))


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
