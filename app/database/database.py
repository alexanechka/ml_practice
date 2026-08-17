from sqlmodel import SQLModel, Session, create_engine, select
from contextlib import contextmanager
from .config import get_settings
from sqlmodel import SQLModel, Session, create_engine
from models.ml_model import MLModel, InputLanguages
from models.user import User, Wallet, Role
from services.auth.hash_password import HashPassword

def get_database_engine():
    """
    Create and configure the SQLAlchemy engine.
    
    Returns:
        Engine: Configured SQLAlchemy engine
    """
    settings = get_settings()
    
    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine

engine = get_database_engine()

def get_session():
    with Session(engine) as session:
        yield session
        
def add_default_models() -> None:
    with Session(engine) as session:
        existing = session.exec(select(MLModel)).first()
        if existing:
            return  

        session.add(MLModel(
            model_description="Summarization model (EN)",
            request_cost=3,
            language=InputLanguages.EN,
        ))
        session.add(MLModel(
            model_description="Summarization model (RU)",
            request_cost=7,
            language=InputLanguages.RU,
        ))
        session.commit()


def add_default_users() -> None:
    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if existing:
            return

        hash_password = HashPassword()

        admin = User(
            email="admin@example.com",
            password=hash_password.create_hash("admin123"),
            wallet=Wallet(balance=0),
            role=Role.ADMIN,
        )
        demo_user = User(
            email="demo@example.com",
            password=hash_password.create_hash("demo12345"),
            wallet=Wallet(balance=50),
            role=Role.USER,
        )

        session.add(admin)
        session.add(demo_user)
        session.commit()


def init_db(drop_all: bool = False) -> None:
    """
    Initialize database schema.
    
    Args:
        drop_all: If True, drops all tables before creation
    
    Raises:
        Exception: Any database-related exception
    """
    try:
        engine = get_database_engine()
        if drop_all:
            SQLModel.metadata.drop_all(engine)
        
        SQLModel.metadata.create_all(engine)
        add_default_models()
        add_default_users()
    except Exception as e:
        raise

