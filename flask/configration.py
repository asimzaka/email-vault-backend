import os
import sys
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from rococo.data import MySqlAdapter
from rococo.messaging import RabbitMqConnection
from flask_cors import CORS
from alembic.config import Config as AlembicConfig
from logging.config import fileConfig
from alembic import command


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(base_dir)

secrets_env = os.path.join(base_dir, '.env.secrets')
if not find_dotenv(secrets_env):
    raise FileNotFoundError(f"Required .env.secrets file not found at {secrets_env}")
load_dotenv(secrets_env)

APP_ENV = os.getenv("APP_ENV", "local").lower()
env_file = os.path.join(base_dir, f"{APP_ENV}.env")
if not find_dotenv(env_file):
    raise FileNotFoundError(f"Environment file for '{APP_ENV}' not found at {env_file}")
load_dotenv(env_file, override=True)

alembic_config = AlembicConfig("alembic.ini")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")
    QUEUE_NAME_PREFIX = os.getenv("QUEUE_NAME_PREFIX")
    EMAIL_TRANSMITTER_QUEUE_NAME = f"{QUEUE_NAME_PREFIX}{os.getenv('EmailServiceProcessor_QUEUE_NAME')}"
    
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USERNAME = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    RABBITMQ_VIRTUAL_HOST = os.getenv("RABBITMQ_VIRTUAL_HOST")
    
    DEBUG = APP_ENV == "local"
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    def __init__(self, app: Flask):
        app.config.from_object(self)
        self.validate_required_vars()
        alembic_config.set_main_option("sqlalchemy.url", self.SQLALCHEMY_DATABASE_URI)
        fileConfig(alembic_config.config_file_name)
    
    @classmethod
    def validate_required_vars(cls):
        required_vars = [
            'SECRET_KEY', 'MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DATABASE', 
            'RABBITMQ_HOST', 'RABBITMQ_USER', 'RABBITMQ_PASSWORD'
        ]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    @staticmethod
    def get_db_connection():
        """Returns a fresh MySQL adapter instance each time it’s called."""
        return MySqlAdapter(
            Config.MYSQL_HOST, Config.MYSQL_PORT, Config.MYSQL_USERNAME,
            Config.MYSQL_PASSWORD, Config.MYSQL_DATABASE
        )

    @classmethod
    def get_rabbit_mq_connection(cls):        
        return RabbitMqConnection(cls.RABBITMQ_HOST, cls.RABBITMQ_PORT, cls.RABBITMQ_USER, cls.RABBITMQ_PASSWORD, cls.RABBITMQ_VIRTUAL_HOST)

    @staticmethod
    def run_migrations():
        alembic_cfg = AlembicConfig("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", Config.SQLALCHEMY_DATABASE_URI)
        command.upgrade(alembic_cfg, "head")
