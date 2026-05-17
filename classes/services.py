from datetime import datetime

from sqlalchemy.orm import Session

from classes.service_galleries import ServiceGalleryClass
from models.service_galleries import ServiceGallery
from models.services import Service
from utils.media_storage import persist_service_gallery_file
from schemas.service_galleries import ServiceGallerySchema
from schemas.services import (
    CreateService,
    CreateServiceGalleryNested,
    ServiceSchema,
    UpdateService,
    UpdateServiceGalleryNested,
)


class ServiceClass:
    def __init__(self, db: Session):
        self.db = db

    def _active_query(self):
        return self.db.query(Service).filter(Service.deleted_date.is_(None))

    def _galleries_for_services(self, service_ids: list[int]) -> dict[int, list[ServiceGallery]]:
        if not service_ids:
            return {}

        galleries = (
            self.db.query(ServiceGallery)
            .filter(
                ServiceGallery.service_id.in_(service_ids),
                ServiceGallery.deleted_date.is_(None),
            )
            .order_by(ServiceGallery.id.asc())
            .all()
        )

        grouped: dict[int, list[ServiceGallery]] = {sid: [] for sid in service_ids}
        for gallery in galleries:
            grouped[gallery.service_id].append(gallery)

        return grouped

    def to_schema(
        self,
        service: Service,
        galleries: list[ServiceGallery] | None = None,
    ) -> ServiceSchema:
        if galleries is None:
            galleries = ServiceGalleryClass(self.db).get_by_service_id(
                service.id,
                limit=500,
            )

        return ServiceSchema(
            id=service.id,
            title=service.title,
            subtitle=service.subtitle,
            description=service.description,
            added_date=service.added_date,
            updated_date=service.updated_date,
            deleted_date=service.deleted_date,
            galleries=[
                ServiceGallerySchema.model_validate(g) for g in galleries
            ],
        )

    def _persist_gallery_files(
        self,
        data: dict,
        *,
        service_id: int,
        previous: ServiceGallery | None = None,
    ) -> dict:
        prev_file1 = previous.file1 if previous else None
        prev_file2 = previous.file2 if previous else None

        if "file1" in data:
            data["file1"] = persist_service_gallery_file(
                data.get("file1"),
                service_id=service_id,
                field="file1",
                previous=prev_file1,
            )
        if "file2" in data:
            data["file2"] = persist_service_gallery_file(
                data.get("file2"),
                service_id=service_id,
                field="file2",
                previous=prev_file2,
            )

        return data

    def _create_galleries(
        self,
        service_id: int,
        galleries: list[CreateServiceGalleryNested],
        now: datetime,
    ) -> None:
        for gallery in galleries:
            data = gallery.model_dump(exclude_none=True)
            data = self._persist_gallery_files(data, service_id=service_id)
            data["service_id"] = service_id
            data.setdefault("added_date", now)
            data.setdefault("updated_date", now)
            self.db.add(ServiceGallery(**data))

    def _sync_galleries(
        self,
        service_id: int,
        galleries: list[UpdateServiceGalleryNested],
        now: datetime,
    ) -> None:
        gallery_class = ServiceGalleryClass(self.db)
        existing = gallery_class.get_by_service_id(service_id, limit=500)
        existing_by_id = {g.id: g for g in existing}
        kept_ids: set[int] = set()

        for item in galleries:
            data = item.model_dump(exclude_unset=True)
            gallery_id = data.pop("id", None)

            if gallery_id is not None:
                db_gallery = existing_by_id.get(gallery_id)
                if db_gallery is None:
                    continue

                update_fields = self._persist_gallery_files(
                    data,
                    service_id=service_id,
                    previous=db_gallery,
                )
                for field, value in update_fields.items():
                    setattr(db_gallery, field, value)

                db_gallery.updated_date = now
                kept_ids.add(gallery_id)
                continue

            create_data = self._persist_gallery_files(
                data.copy(),
                service_id=service_id,
            )
            create_data["service_id"] = service_id
            create_data.setdefault("added_date", now)
            create_data.setdefault("updated_date", now)

            if "gallery_type_id" not in create_data:
                continue

            self.db.add(ServiceGallery(**create_data))

        for gallery_id, db_gallery in existing_by_id.items():
            if gallery_id not in kept_ids:
                db_gallery.deleted_date = now
                db_gallery.updated_date = now

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ServiceSchema]:
        services = (
            self._active_query()
            .order_by(Service.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not services:
            return []

        galleries_map = self._galleries_for_services([s.id for s in services])

        return [
            self.to_schema(service, galleries_map.get(service.id, []))
            for service in services
        ]

    def get_by_id(self, service_id: int) -> ServiceSchema | None:
        service = (
            self._active_query()
            .filter(Service.id == service_id)
            .first()
        )

        if service is None:
            return None

        return self.to_schema(service)

    def store(self, service: CreateService) -> ServiceSchema:
        now = datetime.utcnow()
        data = service.model_dump(exclude_none=True, exclude={"galleries"})
        galleries = service.galleries

        if "added_date" not in data:
            data["added_date"] = now
        if "updated_date" not in data:
            data["updated_date"] = now

        try:
            db_service = Service(**data)
            self.db.add(db_service)
            self.db.flush()

            if galleries:
                self._create_galleries(db_service.id, galleries, now)

            self.db.commit()
            self.db.refresh(db_service)
            return self.to_schema(db_service)
        except Exception:
            self.db.rollback()
            raise

    def update(self, service_id: int, service: UpdateService) -> ServiceSchema | None:
        db_service = (
            self._active_query()
            .filter(Service.id == service_id)
            .first()
        )

        if db_service is None:
            return None

        now = datetime.utcnow()
        data = service.model_dump(exclude_unset=True, exclude={"galleries"})
        galleries = service.galleries

        for field, value in data.items():
            setattr(db_service, field, value)

        db_service.updated_date = now

        try:
            if galleries is not None:
                self._sync_galleries(service_id, galleries, now)

            self.db.commit()
            self.db.refresh(db_service)
            return self.to_schema(db_service)
        except Exception:
            self.db.rollback()
            raise

    def delete(self, service_id: int) -> bool:
        db_service = (
            self._active_query()
            .filter(Service.id == service_id)
            .first()
        )

        if db_service is None:
            return False

        now = datetime.utcnow()
        ServiceGalleryClass(self.db).delete_all_by_service_id(service_id)

        db_service.deleted_date = now
        db_service.updated_date = now

        self.db.commit()

        return True
