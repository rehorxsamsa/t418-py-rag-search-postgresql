from contextlib import contextmanager

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.embedding_dim), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def init_db() -> None:
    """Create tables and the IVFFlat index for fast similarity search."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        # Cosine-distance index; lists tuned for small demo datasets.
        conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS documents_embedding_idx "
            "ON documents USING ivfflat (embedding vector_cosine_ops) "
            "WITH (lists = 100);"
        )
        conn.commit()


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
