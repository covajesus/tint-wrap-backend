import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv(Path(__file__).resolve().parent / ".env")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no está definida. Añádela en backend/.env"
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
