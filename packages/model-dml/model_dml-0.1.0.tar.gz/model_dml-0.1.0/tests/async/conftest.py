import pytest_asyncio
import sqlalchemy


@pytest_asyncio.fixture
async def john(async_fake_session_maker, user):
    stmt = sqlalchemy.insert(user).values(name="John").returning(user.id, user.name)
    async with async_fake_session_maker.begin() as session:
        user = await session.execute(stmt)
        return user.first()


@pytest_asyncio.fixture
async def jane(async_fake_session_maker, user):
    stmt = sqlalchemy.insert(user).values(name="Jane").returning(user.id, user.name)
    async with async_fake_session_maker.begin() as session:
        user = await session.execute(stmt)
        return user.first()
