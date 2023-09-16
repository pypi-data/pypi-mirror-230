import pydantic_settings
import pytest
import pytest_asyncio
import sqlalchemy.ext.asyncio
import sqlalchemy.orm
from fake_session_maker import async_fsm, fsm

import model_dml


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env")

    sqlalchemy_test_url: str
    async_sqlalchemy_test_url: str


settings = Settings()


@pytest.fixture(autouse=True, scope="session")
def db_migrate():
    path = "postgresql://test:test@localhost:5432/test"
    engine = sqlalchemy.create_engine(path, echo=True)
    with engine.connect() as con:
        con.execute(
            sqlalchemy.text(
                'create table if not exists "users" ('
                '   "id" serial constraint users_pk primary key , '
                '   "name" text'
                ");"
            )
        )
        con.commit()
    yield
    with engine.connect() as con:
        con.execute(sqlalchemy.text('drop table "users";'))
        con.commit()


class Namespace:
    session_maker: sqlalchemy.orm.sessionmaker = None
    async_session_maker: sqlalchemy.ext.asyncio.async_sessionmaker = None


class Base(sqlalchemy.orm.DeclarativeBase):
    @classmethod
    def session_maker(cls) -> sqlalchemy.orm.sessionmaker:
        return Namespace.session_maker

    @classmethod
    def async_session_maker(cls) -> sqlalchemy.ext.asyncio.async_sessionmaker:
        return Namespace.async_session_maker


@pytest.fixture
def base():
    return Base


@pytest.fixture
def user(base):
    # fmt: off
    class User(base, model_dml.DML):
        __tablename__ = "users"
        __table_args__ = {"extend_existing": True}
        id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
        name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
            sqlalchemy.String(30))

    # fmt: on

    return User


@pytest.fixture
def fake_session_maker() -> sqlalchemy.orm.sessionmaker:
    with fsm(
        db_url=settings.sqlalchemy_test_url,
        namespace=Namespace,
        symbol_name="session_maker",
        create_engine_kwargs={"echo": True},
    ) as fake_session_maker_:
        yield fake_session_maker_


@pytest_asyncio.fixture
async def async_fake_session_maker() -> sqlalchemy.orm.sessionmaker:
    async with async_fsm(
        db_url=settings.async_sqlalchemy_test_url,
        namespace=Namespace,
        symbol_name="async_session_maker",
        create_engine_kwargs={"echo": True},
    ) as fake_session_maker_:
        yield fake_session_maker_
