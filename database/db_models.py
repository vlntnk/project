from uuid import UUID

from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID, DATE
import uuid
import datetime


Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users table'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = Column(String(128), nullable=False)
    surname = Column(String(256), nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DATE, default=datetime.datetime.utcnow())
    updated_at = Column(DATE, default=datetime.datetime.utcnow())


class Cookies(Base):
    __tablename__ = 'Cookies'

    session_id = Column(String, nullable=False, primary_key=True)
    jwt_token = Column(String, nullable=False)

