import pytest
import sqlalchemy.exc


def test_delete(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))
    result = user.delete([])
    assert result is None

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with pytest.raises(sqlalchemy.exc.NoResultFound), fake_session_maker() as session:
        session.execute(stmt).one()


def test_delete_returning_result(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    user_, *_ = user.delete([], returning=[user.id, user.name])
    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert user_.id == 1
    assert user_.name == "John"

    assert check is None


def test_delete_returning_scalar(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    (name, *_), *_ = user.delete([user.id == 1], returning=[user.name])

    assert name == "John"

    stmt = sqlalchemy.select(user.id, user.name).where(user.id == 1)
    with fake_session_maker() as session:
        check = session.execute(stmt).first()

    assert check is None
