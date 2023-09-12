import os
from datetime import date

import factory
import pytest
from factory.alchemy import SQLAlchemyModelFactory
from flask_bcrypt import generate_password_hash
from pytest_factoryboy import register
from sqlalchemy import create_engine, event

from alembic import command
from alembic.config import Config as AlembicConfig
from pychores import create_app
from pychores.configmodule import Config
from pychores.model import Chore, DeferedSession, Task, User

SessionLocal = DeferedSession.get_session_local(
    Config.get_config("test").SQLALCHEMY_DATABASE_URI
)


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = SessionLocal
        sqlalchemy_session_persistence = "commit"


@pytest.fixture(scope="session")
def connection():
    """
    recreate the database for each test :(
    i'm not smart enough to make the rollback thing works properly
    """
    ini_location = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    sqlalchemy_url = Config.get_config("test").SQLALCHEMY_DATABASE_URI
    alembic_config = AlembicConfig(ini_location)
    alembic_config.set_main_option("sqlalchemy.url", sqlalchemy_url)
    command.upgrade(alembic_config, "head")
    engine = create_engine(Config.get_config("test").SQLALCHEMY_DATABASE_URI)
    connection = engine.connect()
    yield connection
    connection.close()
    command.downgrade(alembic_config, "base")


@pytest.fixture
def app(connection):
    app = create_app("test")
    yield app
    app.db_session.remove()


@pytest.fixture()
def db_session(connection):
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(db_session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    yield session

    SessionLocal.remove()
    transaction.rollback()


@register
class UserFactory(BaseFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    password = factory.Sequence(
        lambda n: generate_password_hash(f"password_{n}").decode("utf-8")
    )
    email = factory.Sequence(lambda n: f"user_{n}@example.com")


@register
class ChoreFactory(BaseFactory):
    class Meta:
        model = Chore

    name = factory.Sequence(lambda n: f"chore_{n}")
    description = factory.Sequence(lambda n: f"description of chore_{n}")
    period = 5
    user = factory.SubFactory(UserFactory)


@register
class TaskFactory(BaseFactory):
    class Meta:
        model = Task

    execution_date = date(year=2020, month=5, day=18)
    chore = factory.SubFactory(ChoreFactory)


@pytest.fixture
def headers():
    mimetype = "application/json"
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype,
    }
    return headers
