import asyncpgsa

from database.db import users
from sqlalchemy import (
            MetaData, Table, Column, ForeignKey,
                Integer, String, DateTime, Date, VARCHAR

        )
from sqlalchemy.sql import select

class User:

    @staticmethod
    async def create_user(db, key, login, password):
        new_user = users.insert().values(key = key, login = login, password = password)
        await db.execute(new_user)

    @staticmethod
    async def get_all_users(db):
        all_user = await db.fetch(
            users.select()
        )
        return all_user

    @staticmethod
    async def get_user_by_id(db, user_id):
        user = await db.fetchrow(
            users.select().where(users.c.id == user_id)
        )
        return user

    @staticmethod
    async def get_user_by_key(db, key):
        user = await db.fetchrow(
            users.select().where(users.c.key == key)
        )
        return user

    @staticmethod
    async def get_user_by_login(db, login):
        user = await db.fetchrow(
            users.select().where(users.c.login == login)
        )
        return user
