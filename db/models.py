import datetime

from sqlalchemy import Column, Integer, Date, VARCHAR, ForeignKey, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column(VARCHAR(50))
    last_name = Column(VARCHAR(50))
    phone_number = Column(VARCHAR(20))
    city = Column(VARCHAR(50))
    telegram_id = Column(Integer, unique=True)
    registration_date = Column(Date, default=datetime.date.today())

    __tablename__ = 'users'


class Cars(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    make = Column(VARCHAR(50))
    model = Column(VARCHAR(50))
    color = Column(VARCHAR(20))
    license_plate = Column(VARCHAR(15))
    year = Column(Integer)

    __tablename__ = 'cars'


class Messages(Base):
    id = Column(Integer, primary_key=True)
    sender_user_id = Column(Integer, ForeignKey('users.id'))
    receiver_user_id = Column(Integer, ForeignKey('users.id'))
    message_text = Column(String)

    __tablename__ = 'messages'
