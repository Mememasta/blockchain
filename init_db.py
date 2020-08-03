import argparse

from config.common import BaseConfig
from database.db import users, construct_db_url
from sqlalchemy import create_engine, MetaData
from security import generate_password_hash, generate_key

def setup_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']
    db_pass = target_config['DB_PASS']

    with engine.connect() as conn:
        teardown_db(executor_config = executor_config,
                     target_config = target_config)

        conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                      (db_name, db_user))

def get_engine(db_config):
    db_url = construct_db_url(db_config)
    engine = create_engine(db_url, isolation_level = "AUTOCOMMIT")
    return engine

def teardown_db(executor_config = None, target_config = None):
    engine = get_engine(executor_config)
    print(engine.connect())

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']

    with engine.connect() as conn:
        conn.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '%s'
              AND pid <> pg_backend_pid();""" % db_name)
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP ROLE IF EXISTS %s" % db_user)

def create_tables(target_config = None):
    engine = get_engine(target_config)

    metadata = MetaData()
    metadata.create_all(bind = engine, tables = [users])

def create_sample_data(target_config=None):
    engine = get_engine(target_config)

    with engine.connect() as conn:
        conn.execute(users.insert(), [
            {'key': str(generate_key('-', '')),
             'login': 'leo',
             'password': generate_password_hash('leo')},
            {'key': str(generate_key('-', '')),
             'login': 'richard',
             'password': generate_password_hash('richard')},
        ])

def drop_tables(target_config = None):
    engine = get_engine(target_config)

    metadata = MetaData()
    metadata.drop_all(bind = engine, tables = [users])

if __name__ == "__main__":
    user_db_config = BaseConfig.load_config('config/user_config.toml')['database']
    admin_db_config = BaseConfig.load_config('config/config.toml')['database']
    print(user_db_config)
    print(admin_db_config)

    parser = argparse.ArgumentParser(description = "Ключи для работы с БД")
    parser.add_argument('-c', '--create', help = "Создать пустую бд и пользователя", action = 'store_true')
    parser.add_argument('-d', '--drop', help = "Удалить бд и роль пользователя", action = 'store_true')
    parser.add_argument('-r', '--recreate', help = "Удалить и пересоздать бд и пользователя", action = 'store_true')
    parser.add_argument('-a', '--all', help = "Создать образец", action = 'store_true')
    args = parser.parse_args()

    if args.create:
        setup_db(executor_config = admin_db_config,
                 target_config = user_db_config)
    elif args.drop:
        teardown_db(executor_config = admin_db_config,
                    target_config = user_db_config)
    elif args.recreate:
        teardown_db(executor_config = admin_db_config,
                    target_config = user_db_config)
        setup_db(executor_config = admin_db_config,
                 target_config = user_db_config)
    elif args.all:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
        create_tables(target_config=user_db_config)
        create_sample_data(target_config=user_db_config)
    else:
        parser.print_help()
