from postgres_table import session_marker, User
from sqlalchemy import select, func

async def insert_new_user_in_table(user_tg_id: int, name: str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('we are here')
        if not needed_data:
            print('Now we are into first function')
            new_us = User(tg_us_id=user_tg_id, user_name=name)
            session.add(new_us)
            await session.commit()


async def check_user_in_table(user_tg_id:int):
    """Функция проверяет есть ли юзер в БД"""
    async with session_marker() as session:
        print("Work check_user Function")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        data = query.one_or_none()
        return data

async def insert_lan(user_id:int, lan:str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        needed_data.lan = lan
        await session.commit()

async def insert_lan_in_spam(user_id:int, lan:str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        needed_data.spam = lan
        await session.commit()

async def insert_timezone(user_id:int, us_tz:str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        needed_data.tz = us_tz
        await session.commit()


async def insert_serialised_note(user_id:int, zametka):  # Можно использовать для хранения индивидуальной базы напоминаний юзера
    async with session_marker() as session:
        print('insert_serialised_note\n\n')
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        needed_data.zametki = zametka
        await session.commit()

async def return_lan(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.lan

async def return_tz(user_id:int):
    async with session_marker() as session:
        print('return tz works')
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.tz

async def return_zametki(user_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_id))
        needed_data = query.scalar()
        return needed_data.zametki


async def get_user_count():
    '''Функция считает общее количество запустивших бота'''
    async with session_marker() as session:
        result = await session.execute(select(func.count(User.index)))
        count = result.scalar()
        return count

async def return_user_wanted_spam():
    '''Функция возвращает список картежей id юзеров, которые хотят получать спам'''
    async with session_marker() as session:
        result = await session.execute(select(User.tg_us_id, User.lan).where(User.spam != ''))
        print('result = ', result)
        return result

