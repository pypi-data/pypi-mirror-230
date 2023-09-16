import pytest


def test_select_all_columns(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    assert user.select() == [(1, "John")]


def test_select_one_column(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    assert user.select(columns=user.name) == ["John"]


def test_select_many_column(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    assert user.select(columns=[user.name, user.id]) == [("John", 1)]


def test_select_empty_columns(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))

    with pytest.raises(ValueError):
        user.select(columns=[])


def test_select_wrong_type_columns(fake_session_maker, user):
    with pytest.raises(TypeError):
        user.select(columns=1)


def test_select_empty_filter(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))
        session.add(user(name="Jane"))

    assert user.select(where=[]) == [(1, "John"), (2, "Jane")]


def test_select_filter(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))
        session.add(user(name="Jane"))

    assert user.select(where=[user.name == "John"]) == [(1, "John")]


def test_select_limit(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))
        session.add(user(name="Jane"))

    assert user.select(limit=1) == [(1, "John")]


def test_select_no_limit(fake_session_maker, user):
    with fake_session_maker.begin() as session:
        session.add(user(name="John"))
        session.add(user(name="Jane"))

    assert user.select(limit=-1) == [(1, "John"), (2, "Jane")]
