import collections.abc
import typing

import pytest


class UserRow(typing.NamedTuple):
    id: int
    name: str


def check_users_sequence(users, *witnesses: UserRow):
    assert isinstance(users, collections.abc.Sequence)
    assert len(users) == len(witnesses)

    for user, witness in zip(users, witnesses):
        assert hasattr(user, "id")
        assert hasattr(user, "name")

        assert isinstance(user.id, int)
        assert user.name == witness.name


@pytest.mark.asyncio
async def test_async_select_all_columns(john: UserRow, user):
    users = await user.async_select()
    check_users_sequence(users, john)


@pytest.mark.asyncio
async def test_async_select_one_column(john: UserRow, user):
    users = await user.async_select(columns=user.name)

    assert isinstance(users, collections.abc.Sequence)
    assert len(users) == 1

    user_name, *_ = users
    assert user_name == john.name


@pytest.mark.asyncio
async def test_async_select_many_column(john: UserRow, user):
    users = await user.async_select(columns=[user.name, user.id])
    user, *_ = users
    assert user == (user.name, user.id)

    check_users_sequence(users, john)


@pytest.mark.asyncio
async def test_async_select_empty_columns(user):
    with pytest.raises(ValueError):
        await user.async_select(columns=[])


@pytest.mark.asyncio
async def test_async_select_wrong_type_columns(async_fake_session_maker, user):
    with pytest.raises(TypeError):
        await user.async_select(columns=1)


@pytest.mark.asyncio
async def test_async_select_empty_filter(john: UserRow, jane: UserRow, user):
    users = await user.async_select(where=[])
    check_users_sequence(users, john, jane)


@pytest.mark.asyncio
async def test_async_select_filter(john: UserRow, jane: UserRow, user):
    users = await user.async_select(where=[user.name == john.name])
    check_users_sequence(users, john)


@pytest.mark.asyncio
async def test_async_select_limit(john: UserRow, jane: UserRow, user):
    users = await user.async_select(limit=1)
    check_users_sequence(users, john)


@pytest.mark.asyncio
async def test_async_select_no_limit(john: UserRow, jane: UserRow, user):
    users = await user.async_select(limit=None)
    check_users_sequence(users, john, jane)
