from sqlalchemy import Column, String, Integer, DECIMAL, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID, DATE, TIME, TEXT, ARRAY
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
    notifications = Column(Boolean, default=True)
    categories = Column(ARRAY(String), nullable=False)
    radius = Column(Integer, default=100)
    created_at = Column(DATE, default=datetime.datetime.utcnow())
    updated_at = Column(DATE, default=datetime.datetime.utcnow())


class Cookies(Base):
    __tablename__ = 'Cookies'

    session_id = Column(String, nullable=False, primary_key=True)
    jwt_token = Column(String, nullable=False)


class OneTimeSales(Base):
    __tablename__ = 'One-time sales'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    percentage = Column(Integer, nullable=False)
    comment = Column(TEXT)
    start_at = Column(TIME, default=datetime.datetime.utcnow())
    end_at = Column(TIME, nullable=False)
    date = Column(DATE, nullable=False)
    categories = Column(ARRAY(String), nullable=False)
    creator = Column(String, nullable=False)
    coordinates = Column(ARRAY(DECIMAL), nullable=False)


class RepeatedSales(Base):
    __tablename__ = 'Repeated sales'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    percentage = Column(Integer, nullable=False)
    comment = Column(TEXT)
    start_at = Column(TIME, nullable=False)
    end_at = Column(TIME, nullable=False)
    weekday = Column(String, nullable=False)
    categories = Column(ARRAY(String), nullable=False)
    creator = Column(String, nullable=False)
    coordinates = Column(ARRAY(DECIMAL), nullable=False)

