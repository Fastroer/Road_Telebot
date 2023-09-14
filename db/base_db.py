import datetime
import logging

from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config
from db.models import Base, User, Cars, Messages


async def create_database_connection():
    logging.debug("Начало функции create_database_connection()")

    engine = create_async_engine(
        f'postgresql+asyncpg://{config.db_user}:{config.db_password}@'
        f'{config.db_host}:{config.db_port}/{config.db_name}'
    )

    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with engine.begin() as conn:
        logging.debug("Создание таблиц в базе данных")
        await conn.run_sync(Base.metadata.create_all)

    logging.debug("Завершение функции create_database_connection()")

    return engine, async_session


async def is_user_registered(telegram_id):
    logging.debug("Начало функции is_user_registered()")
    engine, async_session = await create_database_connection()

    async with async_session() as session:
        existing_user = await session.execute(select(User).where(User.telegram_id == telegram_id))

        logging.debug("Завершение функции is_user_registered()")

        return existing_user.scalar()


async def get_user_id(telegram_id):
    logging.debug("Начало функции get_user_id()")
    engine, async_session = await create_database_connection()

    async with async_session() as session:
        existing_user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        logging.debug("Завершение функции get_user_id()")
        return existing_user.scalar().id


async def register_user(first_name, last_name, phone_number, city, telegram_id):
    logging.debug("Начало функции register_user()")

    engine, async_session = await create_database_connection()

    async with async_session() as session:
        async with session.begin():
            logging.debug("Добавление пользователя в базу данных")
            user = User(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                city=city,
                telegram_id=telegram_id,
                registration_date=datetime.date.today()
            )
            session.add(user)

    logging.debug("Завершение функции register_user()")


async def register_user_car(user_id, make):
    logging.debug("Начало функции register_user_car()")

    engine, async_session = await create_database_connection()

    async with async_session() as session:
        async with session.begin():
            logging.debug("Добавление машины в базу данных")
            car = Cars(
                make=make,
                user_id=user_id
            )
            session.add(car)

    logging.debug("Завершение функции register_user_car()")


async def update_user_car(data: list, user_id):
    logging.debug("Начало функции update_user_car()")

    engine, async_session = await create_database_connection()

    async with async_session() as session:
        car = await session.execute(select(Cars).where(Cars.user_id == user_id))
        logging.debug("Изменение данные в update_user_car()")
        if data[0] == 'model':
            car.scalar().model = data[1]
        elif data[0] == 'color':
            car.scalar().color = data[1]
        elif data[0] == 'license_plate':
            car.scalar().license_plate = data[1]
        elif data[0] == 'year':
            car.scalar().year = int(data[1])
        await session.commit()
    logging.debug("Завершение функции update_user_car()")


async def delete_user(user_id):
    logging.debug("Начало функции delete_user()")
    engine, async_session = await create_database_connection()

    async with async_session() as session:
        await session.execute(delete(Cars).where(Cars.user_id == user_id))
        await session.execute(
            delete(Messages).where(or_(Messages.receiver_user_id == user_id, Messages.sender_user_id == user_id)))
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
    logging.debug("Завершение функции delete_user()")


async def driver_search(license_plate):
    logging.debug("Начало функции driver_search()")
    engine, async_session = await create_database_connection()

    async with async_session() as session:
        query = select(Cars).where(Cars.license_plate == license_plate)
        results = await session.execute(query)
        cars = [row[0] for row in results.all()]
        users_list = list()
        for car in cars:
            user_query = select(User).where(User.id == car.user_id)
            user_results = await session.execute(user_query)
            user_data = [row[0] for row in user_results.all()]
            for data in user_data:
                users_list.append(' '.join([data.first_name, data.last_name, data.phone_number]))
                users_list.append(data.id)
        logging.debug("Завершение функции driver_search()")
        return users_list


async def add_message(sender_user_id, receiver_user_id, message_text):
    logging.debug("Начало функции add_message()")

    engine, async_session = await create_database_connection()

    async with async_session() as session:
        async with session.begin():
            logging.debug("Добавление сообщения в базу данных")
            message = Messages(
                sender_user_id=sender_user_id,
                receiver_user_id=receiver_user_id,
                message_text=message_text,
            )
            session.add(message)

    logging.debug("Завершение функции add_message()")


async def your_messages(user_id):
    logging.debug("Начало функции your_messages()")
    engine, async_session = await create_database_connection()

    async with async_session() as session:
        query = select(Messages).where(Messages.receiver_user_id == user_id)
        results = await session.execute(query)
        data_message = [row[0] for row in results.all()]
        users_list = list()
        for data in data_message:
            user_query = select(User).where(User.id == data.sender_user_id)
            user_results = await session.execute(user_query)
            user_data = [row[0] for row in user_results.all()]
            for data_us in user_data:
                users_list.append(
                    [' '.join([data_us.first_name, data_us.last_name, data_us.phone_number]), data.message_text])
        logging.debug("Завершение функции your_messages()")
        return users_list
