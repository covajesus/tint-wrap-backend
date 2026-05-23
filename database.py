import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

_ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_FILE)


def _env(key: str) -> str | None:
    value = os.getenv(key)
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


SQLALCHEMY_DATABASE_URL = _env("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL no está en {_ENV_FILE}. "
        "Ejemplo: DATABASE_URL=mysql+pymysql://usuario:pass@localhost:3306/tw"
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

        if dialect == "mysql":
            conn.execute(
                text(
                    "UPDATE blogs SET added_date = COALESCE(added_date, updated_date, UTC_TIMESTAMP()) "
                    "WHERE added_date IS NULL"
                )
            )
            conn.execute(
                text(
                    "UPDATE blogs SET updated_date = COALESCE(updated_date, added_date, UTC_TIMESTAMP()) "
                    "WHERE updated_date IS NULL"
                )
            )
        elif dialect == "sqlite":
            conn.execute(
                text(
                    "UPDATE blogs SET added_date = COALESCE(added_date, updated_date, datetime('now')) "
                    "WHERE added_date IS NULL"
                )
            )
            conn.execute(
                text(
                    "UPDATE blogs SET updated_date = COALESCE(updated_date, added_date, datetime('now')) "
                    "WHERE updated_date IS NULL"
                )
            )
        else:
            conn.execute(
                text(
                    "UPDATE blogs SET added_date = COALESCE(added_date, updated_date, CURRENT_TIMESTAMP) "
                    "WHERE added_date IS NULL"
                )
            )
            conn.execute(
                text(
                    "UPDATE blogs SET updated_date = COALESCE(updated_date, added_date, CURRENT_TIMESTAMP) "
                    "WHERE updated_date IS NULL"
                )
            )


def ensure_sliders_schema() -> None:
    """Migra sliders a columnas slider (foto) y url (enlace al hacer clic)."""
    from sqlalchemy import inspect, text

    insp = inspect(engine)
    if "sliders" not in insp.get_table_names():
        return

    columns = {col["name"] for col in insp.get_columns("sliders")}
    dialect = engine.dialect.name
    had_legacy_media = "slider_image_video" in columns
    had_legacy_url = "main_button_url" in columns
    had_legacy_url2 = "second_button_url" in columns

    with engine.begin() as conn:
        if "slider" not in columns:
            if dialect == "mysql":
                conn.execute(text("ALTER TABLE sliders ADD COLUMN slider TEXT NULL"))
            else:
                conn.execute(text("ALTER TABLE sliders ADD COLUMN slider TEXT"))

        if "url" not in columns:
            if dialect == "mysql":
                conn.execute(
                    text("ALTER TABLE sliders ADD COLUMN url VARCHAR(500) NULL")
                )
            else:
                conn.execute(text("ALTER TABLE sliders ADD COLUMN url VARCHAR(500)"))

        if had_legacy_media:
            conn.execute(
                text(
                    "UPDATE sliders SET slider = slider_image_video "
                    "WHERE slider IS NULL AND slider_image_video IS NOT NULL"
                )
            )

        if had_legacy_url:
            conn.execute(
                text(
                    "UPDATE sliders SET url = main_button_url "
                    "WHERE url IS NULL AND main_button_url IS NOT NULL "
                    "AND TRIM(main_button_url) <> ''"
                )
            )
        if had_legacy_url2:
            conn.execute(
                text(
                    "UPDATE sliders SET url = second_button_url "
                    "WHERE url IS NULL AND second_button_url IS NOT NULL "
                    "AND TRIM(second_button_url) <> ''"
                )
            )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
