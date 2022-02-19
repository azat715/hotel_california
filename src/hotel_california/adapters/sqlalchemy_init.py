from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hotel_california.config import get_settings

settings = get_settings()

engine = create_engine(settings.DB.url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
