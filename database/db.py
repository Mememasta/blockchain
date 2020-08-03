import asyncpgsa

from datetime import datetime
from config.common import BaseConfig

from sqlalchemy import (
        MetaData, VARCHAR, Table, Column, ForeignKey,
        Integer, String, DateTime
        )
from sqlalchemy import select

metadata = MetaData()

users = Table(
        'users', metadata,

        Column('id', Integer, primary_key = True),
        Column('key', VARCHAR(1024), unique = True, nullable = False),
        Column('login', VARCHAR(2048), unique = False, nullable = False),
        Column('password', VARCHAR(2048), unique = False, nullable = False)

        )

async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = await asyncpgsa.create_pool(dsn = dsn)
    app['db'] = pool
    return pool

def construct_db_url(config):
    DSN = "postgresql://{host}:{port}/{datebase}?user={user}&password={password}"
    return DSN.format(
            user = config['DB_USER'],
            password = config['DB_PASS'],
            datebase = config['DB_NAME'],
            host = config['DB_HOST'],
            port = config['DB_PORT']
            )
