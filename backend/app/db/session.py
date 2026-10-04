from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

class Base(DeclarativeBase):
    pass

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    from sqlalchemy import text
    from app.models import UserProfile, Job, Application
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for table, col, col_type in [
            ("user_profiles", "master_cv_pdf_path", "VARCHAR(255) DEFAULT 'uploads/mastercv.pdf'"),
            ("user_profiles", "saved_tailored_cvs", "JSON DEFAULT '[]'"),
            ("jobs", "is_wishlisted", "BOOLEAN DEFAULT 0"),
            ("jobs", "recently_browsed", "BOOLEAN DEFAULT 0"),
            ("jobs", "last_browsed_at", "DATETIME"),
            ("applications", "is_wishlisted", "BOOLEAN DEFAULT 0"),
            ("applications", "recently_browsed", "BOOLEAN DEFAULT 0"),
            ("applications", "last_browsed_at", "DATETIME"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
