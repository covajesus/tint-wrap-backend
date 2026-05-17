import os

from sqlalchemy.orm import Session

from classes.users import UserClass


def seed_default_admin(db: Session) -> None:
    """Crea el primer usuario si la tabla users está vacía."""
    if UserClass(db).count() > 0:
        return

    email = os.getenv("ADMIN_EMAIL", "admin@tintwrap.com").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    full_name = os.getenv("ADMIN_FULL_NAME", "Administrador").strip() or None

    if not email or not password:
        return

    UserClass(db).create_user(
        email=email,
        password=password,
        full_name=full_name,
        is_active=True,
    )
