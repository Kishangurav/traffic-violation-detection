import os
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=_now)
    camera_id = Column(String(32), default="cam1")
    vehicle_id = Column(Integer, index=True)
    violation_type = Column(String(32), index=True)
    speed = Column(Float, nullable=True)
    plate = Column(String(20), nullable=True)
    frame_number = Column(Integer, nullable=True)
    image_path = Column(String(255), nullable=True)
    clip_path = Column(String(255), nullable=True)


class ViolationDB:
    def __init__(self, url="sqlite:///output/violations.db"):
        kwargs = {}
        if url.startswith("sqlite:///"):
            folder = os.path.dirname(url.replace("sqlite:///", "", 1))
            if folder:
                os.makedirs(folder, exist_ok=True)
            kwargs["connect_args"] = {"check_same_thread": False}

        self.engine = create_engine(url, **kwargs)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add(self, **fields) -> int:
        with self.Session() as session:
            row = Violation(**fields)
            session.add(row)
            session.commit()
            return row.id

    def list_recent(self, limit=50):
        with self.Session() as session:
            return (
                session.query(Violation)
                .order_by(Violation.id.desc())
                .limit(limit)
                .all()
            )