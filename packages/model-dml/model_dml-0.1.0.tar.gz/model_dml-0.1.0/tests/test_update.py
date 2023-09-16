import pytest
import sqlalchemy


def test_update(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    user.update([user.id == 1], {"name": "Jane"})
    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert check.id == 1
    assert check.name == "Jane"


def test_update_empty_returning_rollback(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    with pytest.raises(ValueError):
        user.update([user.id == 1], {"name": "Jane"}, returning=())

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()
        assert check.name == "John"


def test_update_returning_tuples(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    user_, *_ = user.update(
        [user.id == 1], {"name": "Jane"}, returning=(user.id, user.name)
    )
    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert user_.id == check.id == 1
    assert user_.name == check.name == "Jane"
    assert user_ == (1, "Jane")


def test_update_returning_entity(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    (name, *_), *_ = user.update(
        [user.id == 1], {"name": "Jane"}, returning=(user.name,)
    )

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert check.id == 1
    assert name == check.name == "Jane"
