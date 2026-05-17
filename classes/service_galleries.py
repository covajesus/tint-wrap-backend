from datetime import datetime

from sqlalchemy.orm import Session

from models.service_galleries import ServiceGallery
from schemas.service_galleries import CreateServiceGallery, UpdateServiceGallery
from utils.media_storage import (
    delete_local_media,
    delete_service_upload_folder,
    persist_service_gallery_file,
)


class ServiceGalleryClass:
    def __init__(self, db: Session):
        self.db = db

    def _active_query(self):
        return self.db.query(ServiceGallery).filter(
            ServiceGallery.deleted_date.is_(None)
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ServiceGallery]:
        return (
            self._active_query()
            .order_by(ServiceGallery.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, gallery_id: int) -> ServiceGallery | None:
        return (
            self._active_query()
            .filter(ServiceGallery.id == gallery_id)
            .first()
        )

    def get_by_service_id(
        self,
        service_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ServiceGallery]:
        return (
            self._active_query()
            .filter(ServiceGallery.service_id == service_id)
            .order_by(ServiceGallery.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _persist_files(
        self,
        data: dict,
        *,
        service_id: int,
        previous: ServiceGallery | None = None,
    ) -> dict:
        if "file1" in data:
            data["file1"] = persist_service_gallery_file(
                data.get("file1"),
                service_id=service_id,
                field="file1",
                previous=previous.file1 if previous else None,
            )
        if "file2" in data:
            data["file2"] = persist_service_gallery_file(
                data.get("file2"),
                service_id=service_id,
                field="file2",
                previous=previous.file2 if previous else None,
            )
        return data

    def store(self, gallery: CreateServiceGallery) -> ServiceGallery:
        now = datetime.utcnow()
        data = gallery.model_dump(exclude_none=True)
        data = self._persist_files(data, service_id=int(data["service_id"]))

        if "added_date" not in data:
            data["added_date"] = now
        if "updated_date" not in data:
            data["updated_date"] = now

        db_gallery = ServiceGallery(**data)

        self.db.add(db_gallery)
        self.db.commit()
        self.db.refresh(db_gallery)

        return db_gallery

    def update(
        self,
        gallery_id: int,
        gallery: UpdateServiceGallery,
    ) -> ServiceGallery | None:
        db_gallery = self.get_by_id(gallery_id)

        if db_gallery is None:
            return None

        data = gallery.model_dump(exclude_unset=True)
        service_id = int(data.get("service_id", db_gallery.service_id))
        data = self._persist_files(
            data,
            service_id=service_id,
            previous=db_gallery,
        )

        for field, value in data.items():
            setattr(db_gallery, field, value)

        db_gallery.updated_date = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_gallery)

        return db_gallery

    def delete(self, gallery_id: int) -> bool:
        db_gallery = self.get_by_id(gallery_id)

        if db_gallery is None:
            return False

        now = datetime.utcnow()
        delete_local_media(db_gallery.file1)
        delete_local_media(db_gallery.file2)
        db_gallery.deleted_date = now
        db_gallery.updated_date = now

        self.db.commit()

        return True

    def delete_all_by_service_id(self, service_id: int) -> int:
        """Borrado lógico de todas las galerías del servicio (activas o no)."""
        now = datetime.utcnow()
        galleries = (
            self.db.query(ServiceGallery)
            .filter(ServiceGallery.service_id == service_id)
            .all()
        )

        count = 0
        for gallery in galleries:
            if gallery.deleted_date is not None:
                continue

            delete_local_media(gallery.file1)
            delete_local_media(gallery.file2)
            gallery.deleted_date = now
            gallery.updated_date = now
            count += 1

        delete_service_upload_folder(service_id)
        return count
