import pytest
import sqlalchemy


def test_insert(fake_session_maker, user):
    user.insert({"name": "John"})

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert check.id == 1
    assert check.name == "John"


def test_insert_no_returning(fake_session_maker, user):
    with pytest.raises(ValueError):
        user.insert({"name": "John"}, returning=[])

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert check is None


def test_insert_entity_as_row(fake_session_maker, user):
    id_, *_ = user.insert({"name": "John"}, returning=[user.id])

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert id_ == check.id == 1


def test_insert_scalar(fake_session_maker, user):
    name = user.insert({"name": "John"}, returning=user.name)

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert check.id == 1
    assert name == check.name == "John"


def test_insert_result(fake_session_maker, user):
    user_ = user.insert({"name": "John"}, returning=[user.id, user.name])

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert user_.id == check.id == 1
    assert user_.name == check.name == "John"
