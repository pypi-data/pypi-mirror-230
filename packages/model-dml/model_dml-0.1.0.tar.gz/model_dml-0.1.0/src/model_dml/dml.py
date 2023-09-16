from __future__ import annotations

import collections.abc
import typing

import sqlalchemy.ext.asyncio
import sqlalchemy.orm

SingleExecuteParams = typing.Mapping[str, typing.Any]
MultiExecuteParams = typing.Sequence[SingleExecuteParams]
AnyExecuteParams = typing.Union[MultiExecuteParams, SingleExecuteParams]

COLUMNS_CLAUSE_ARGUMENT = sqlalchemy.orm.InstrumentedAttribute


class SessionMakerMixin:
    @classmethod
    def session_maker(cls) -> sqlalchemy.orm.sessionmaker:
        raise NotImplementedError(
            """
Inherit from Base first,
and implement @classmethod session_maker() in the DeclarativeBase of your models:

class Base(sa.orm.DeclarativeBase):
    @classmethod
    def session_maker(cls) -> sqlalchemy.orm.sessionmaker:
        return <namespace>.session_maker

class User(dal_poc.DML, Base): ...
            """
        )

    @classmethod
    def async_session_maker(cls) -> sqlalchemy.ext.asyncio.async_sessionmaker:
        raise NotImplementedError(
            """
Inherit from Base first, and implement @classmethod async_session_maker() in the
DeclarativeBase of your models:

class Base(sa.orm.DeclarativeBase):
    @classmethod
    def async_session_maker(cls) -> sqlalchemy.ext.asyncio.async_sessionmaker:
        return <namespace>.async_session_maker

class User(dal_poc.DML, Base): ...
            """
        )


class Select(SessionMakerMixin):
    @classmethod
    async def _async_select_result(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
        limit: int | None,
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        """
        Select rows of columns of a table.
        A default limit of 500 is applied to prevent accidental large queries.

        >>> User._select_result()
        [(1, 'Jane'), (2, 'John')]
        >>> User._select_result(columns=[User.name, User.id])
        [('Jane', 1), ('John', 2)]
        >>> User._select_result(where=[User.name == 'John'])
        [(2, 'John')]
        >>> User._select_result(limit=1)
        [(1, 'Jane')]
        >>> User._select_result(limit=None)
        [(1, 'Jane'), (2, 'John')]

        >>> User._select_result(limit=1)[0].name
        'Jane'

        :param where: Mandatory where clause, explicit empty where clause is []. Default
            doesn't filter.
        :param columns: None for all columns, a specific column, or a non-empty sequence
            of columns. Default is None.
        :param limit: None for no limit, 0 for no rows, >0 for a limit. Default is 500.
        :return: a sequence of rows of selected columns
        """
        stmt = sqlalchemy.select(*columns).where(*where).limit(limit)
        async with cls.async_session_maker()() as session:  # type: ignore
            return (await session.execute(stmt)).all()

    @classmethod
    async def _async_select_scalar(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: COLUMNS_CLAUSE_ARGUMENT,
        limit: int | None,
    ) -> collections.abc.Sequence[typing.Any]:
        """
        Select a single column of a table.
        The column's values are returned as sequence of values instead of sequence of
            rows.

        >>> User._select_scalar(columns=User.name)
        ['Jane', 'John']
        >>> User._select_scalar(columns=User.name, where=[User.name == 'John'])
        ['John']
        >>> User._select_scalar(columns=User.name, limit=1)
        ['Jane']
        >>> User._select_scalar(columns=User.name, limit=None)
        ['Jane', 'John']

        :param where: mandatory where clause, explicit empty where clause is []. Default
            doesn't filter.
        :param columns: None for all columns, a specific column, or a non-empty sequence
            of columns. Default is None.
        :param limit: None for no limit, 0 for no rows, >0 for a limit. Default is 500.
        :return: a sequence of scalars of a single column
        """
        stmt = sqlalchemy.select(columns).where(*where).limit(limit)
        async with cls.async_session_maker()() as session:  # type: ignore
            return (await session.scalars(stmt)).all()

    @classmethod
    @typing.overload
    async def async_select(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
        limit: int | None,
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        ...

    @classmethod
    @typing.overload
    async def async_select(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: COLUMNS_CLAUSE_ARGUMENT,
        limit: int | None,
    ) -> collections.abc.Sequence[typing.Any]:
        ...

    @classmethod
    async def async_select(
        cls,
        where: typing.Union[
            collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]], None
        ] = None,
        columns: typing.Union[
            collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
            COLUMNS_CLAUSE_ARGUMENT,
            None,
        ] = None,
        limit: int | None = 500,
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row],
        collections.abc.Sequence[typing.Any],
    ]:
        """
        Select rows of columns or scalars of a single column of a table.
        A default limit of 500 is applied to prevent accidental large queries.

        >>> await User.async_select()
        [(1, 'Jane'), (2, 'John')]
        >>> await User.async_select(columns=[User.name, User.id])
        [('Jane', 1), ('John', 2)]
        >>> await User.async_select(columns=[User.name])
        [('Jane',), ('John',)]
        >>> await User.async_select(where=[User.name == 'John'])
        [(2, 'John')]
        >>> await User.async_select(limit=1)
        [(1, 'Jane')]
        >>> await User.async_select(limit=None)
        [(1, 'Jane'), (2, 'John')]

        >>> await User.async_select(columns=User.name)
        ['Jane', 'John']
        >>> await User.async_select(columns=User.name, where=[User.name == 'John'])
        ['John']
        >>> await User.async_select(columns=User.name, limit=1)
        ['Jane']
        >>> await User.async_select(columns=User.name, limit=None)
        ['Jane', 'John']

        >>> await User.async_select(limit=1)[0].name
        'Jane'
        >>> await User.async_select(columns=[User.name])[0].name  # Get a list of rows
        'Jane'
        >>> await User.async_select(columns=User.name)[0]  # Get a list of names
        'Jane'

        :param where: mandatory where clause, explicit empty where clause is []. Default
            doesn't filter.
        :param columns: None for all columns, a specific column, or a non-empty sequence
            of columns. Default is None.
        :param limit: None for no limit, 0 for no rows, >0 for a limit. Default is 500.
        :return: a sequence of rows of selected columns or a sequence of scalars of a
            single column
        :raises ValueError: if columns is an empty sequence
        :raises TypeError: if columns is not None, a specific column, or a non-empty
            sequence
        """
        if where is None:
            where = []

        if isinstance(columns, collections.abc.Sequence) and len(columns) == 0:
            raise ValueError(
                "columns must be None, a specific column, or a non-empty sequence"
            )

        if isinstance(columns, collections.abc.Sequence):
            return await cls._async_select_result(where, columns, limit)

        if isinstance(columns, COLUMNS_CLAUSE_ARGUMENT):
            return await cls._async_select_scalar(where, columns, limit)

        if columns is None:
            return await cls._async_select_result(
                where,
                cls.__table__.columns,  # type: ignore
                limit,
            )

        raise TypeError(
            f"columns must be None, a specific column, or a non-empty sequence; "
            f"got {columns!r}"
        )

    @classmethod
    def _select_result(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
        limit: int | None,
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        """
        Select rows of columns of a table.
        A default limit of 500 is applied to prevent accidental large queries.

        >>> User._select_result()
        [(1, 'Jane'), (2, 'John')]
        >>> User._select_result(columns=[User.name, User.id])
        [('Jane', 1), ('John', 2)]
        >>> User._select_result(where=[User.name == 'John'])
        [(2, 'John')]
        >>> User._select_result(limit=1)
        [(1, 'Jane')]
        >>> User._select_result(limit=None)
        [(1, 'Jane'), (2, 'John')]

        >>> User._select_result(limit=1)[0].name
        'Jane'

        :param where: Mandatory where clause, explicit empty where clause is []. Default
            doesn't filter.
        :param columns: None for all columns, a specific column, or a non-empty sequence
            of columns. Default is None.
        :param limit: None for no limit, 0 for no rows, >0 for a limit. Default is 500.
        :return: a sequence of rows of selected columns
        """
        stmt = sqlalchemy.select(*columns).where(*where).limit(limit)
        with cls.session_maker()() as session:
            return session.execute(stmt).all()

    @classmethod
    def _select_scalar(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: COLUMNS_CLAUSE_ARGUMENT,
        limit: int | None,
    ) -> collections.abc.Sequence[typing.Any]:
        """
        Select a single column of a table.
        The column's values are returned as sequence of values instead of sequence of
            rows.

        >>> User._select_scalar(columns=User.name)
        ['Jane', 'John']
        >>> User._select_scalar(columns=User.name, where=[User.name == 'John'])
        ['John']
        >>> User._select_scalar(columns=User.name, limit=1)
        ['Jane']
        >>> User._select_scalar(columns=User.name, limit=None)
        ['Jane', 'John']

        :param where: mandatory where clause, explicit empty where clause is []. Default
            doesn't filter.
        :param columns: None for all columns, a specific column, or a non-empty sequence
            of columns. Default is None.
        :param limit: None for no limit, 0 for no rows, >0 for a limit. Default is 500.
        :return: a sequence of scalars of a single column
        """
        stmt = sqlalchemy.select(columns).where(*where).limit(limit)
        with cls.session_maker()() as session:
            return session.scalars(stmt).all()

    @classmethod
    @typing.overload
    def select(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
        limit: int | None,
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        ...

    @classmethod
    @typing.overload
    def select(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        columns: COLUMNS_CLAUSE_ARGUMENT,
        limit: int | None,
    ) -> collections.abc.Sequence[typing.Any]:
        ...

    @classmethod
    def select(
        cls,
        where: typing.Union[
            collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]], None
        ] = None,
        columns: typing.Union[
            collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
            COLUMNS_CLAUSE_ARGUMENT,
            None,
        ] = None,
        limit: int | None = 500,
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row],
        collections.abc.Sequence[typing.Any],
    ]:
        """
        Select rows of columns or scalars of a single column of a table.
        A default limit of 500 is applied to prevent accidental large queries.

        >>> User.select()
        [(1, 'Jane'), (2, 'John')]
        >>> User.select(columns=[User.name, User.id])
        [('Jane', 1), ('John', 2)]
        >>> User.select(columns=[User.name])
        [('Jane',), ('John',)]
        >>> User.select(where=[User.name == 'John'])
        [(2, 'John')]
        >>> User.select(limit=1)
        [(1, 'Jane')]
        >>> User.select(limit=None)
        [(1, 'Jane'), (2, 'John')]

        >>> User.select(columns=User.name)
        ['Jane', 'John']
        >>> User.select(columns=User.name, where=[User.name == 'John'])
        ['John']
        >>> User.select(columns=User.name, limit=1)
        ['Jane']
        >>> User.select(columns=User.name, limit=None)
        ['Jane', 'John']

        >>> User.select(limit=1)[0].name
        'Jane'
        >>> User.select(columns=[User.name])[0].name  # Get a list of rows
        'Jane'
        >>> User.select(columns=User.name)[0]  # Get a list of names
        'Jane'

        :param where: mandatory where clause, explicit empty where clause is []. Default
            doesn't filter.
        :param columns: None for all columns, a specific column, or a non-empty sequence
            of columns. Default is None.
        :param limit: None for no limit, 0 for no rows, >0 for a limit. Default is 500.
        :return: a sequence of rows of selected columns or a sequence of scalars of a
            single column
        :raises ValueError: if columns is an empty sequence
        :raises TypeError: if columns is not None, a specific column, or a non-empty
            sequence
        """
        if where is None:
            where = []

        if isinstance(columns, collections.abc.Sequence) and len(columns) == 0:
            raise ValueError(
                "columns must be None, a specific column, or a non-empty sequence"
            )

        if isinstance(columns, collections.abc.Sequence):
            return cls._select_result(where, columns, limit)

        if isinstance(columns, COLUMNS_CLAUSE_ARGUMENT):
            return cls._select_scalar(where, columns, limit)

        if columns is None:
            return cls._select_result(
                where,
                cls.__table__.columns,  # type: ignore
                limit,
            )

        raise TypeError(
            f"columns must be None, a specific column, or a non-empty sequence; "
            f"got {columns!r}"
        )


class Insert(SessionMakerMixin):
    @classmethod
    def _insert_no_returning(cls, values: AnyExecuteParams) -> None:
        """insert a row into a table without returning anything

        >>> User._insert_no_returning({'name': 'Jane'})
        >>> User._insert_no_returning([{'name': 'Jane'}, {'name': 'John'}])

        :param values: values to insert into the table as a dictionary or a sequence of
            dictionaries.
        :return: only None is returned
        """
        stmt = sqlalchemy.insert(cls)
        with cls.session_maker().begin() as session:
            session.execute(stmt, values)

    @classmethod
    def _one_insert_returning_result(
        cls,
        values: SingleExecuteParams,
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> sqlalchemy.Row:
        """insert a row into a table and return a single row of selected columns

        >>> User._one_insert_returning_result({'name': 'Jane'}, [User.id])
        (1,)
        >>> User._one_insert_returning_result({'name': 'Jane'}, [User.id, User.name])
        (1, 'Jane')

        :param values: row to insert into the table
        :param returning: selected columns of the inserted row to return. Cannot be
            empty.
        :return: row of selected columns of the inserted row
        """
        stmt = sqlalchemy.insert(cls).returning(*returning)
        with cls.session_maker().begin() as session:
            return session.execute(stmt, values).first()

    @classmethod
    def _many_insert_returning_result(
        cls,
        values: MultiExecuteParams,
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        """ insert rows into a table and return a sequence of rows of selected columns

        >>> User._many_insert_returning_result([{'name': 'Jane'}, {'name': 'John'}], \
                                               [User.id])
        [(1,), (2,)]
        >>> User._many_insert_returning_result([{'name': 'Jane'}, {'name': 'John'}], \
                                               [User.id, User.name])
        [(1, 'Jane'), (2, 'John')]

        :param values: rows to insert into the table
        :param returning: selected columns of inserted rows to return. Cannot be empty.
        :return: rows of selected columns of inserted rows
        """
        stmt = sqlalchemy.insert(cls).returning(*returning)
        with cls.session_maker().begin() as session:
            return session.execute(stmt, values).all()

    @classmethod
    def _one_insert_returning_scalar(
        cls,
        values: SingleExecuteParams,
        returning: COLUMNS_CLAUSE_ARGUMENT,
    ) -> typing.Any:
        """insert a row into a table and return the value of a single selected column

        >>> User._one_insert_returning_scalar({'name': 'Jane'}, User.id)
        1
        >>> User._one_insert_returning_scalar({'name': 'Jane'}, User.name)
        'Jane'

        :param values: row to insert into the table
        :param returning: selected column of the inserted row to return
        :return: value of selected column of the inserted row
        """
        stmt = sqlalchemy.insert(cls).returning(returning)
        with cls.session_maker().begin() as session:
            result = session.scalars(stmt, values)
            return result.first()

    @classmethod
    def _many_insert_returning_scalar(
        cls,
        values: MultiExecuteParams,
        returning: COLUMNS_CLAUSE_ARGUMENT,
    ) -> collections.abc.Sequence[typing.Any]:
        """insert rows into a table and return a sequence of values of a single selected
            column

        >>> User._many_insert_returning_scalar([{'name': 'Jane'}, {'name': 'John'}], \
                                               User.id)
        [1, 2]
        >>> User._many_insert_returning_scalar([{'name': 'Jane'}, {'name': 'John'}], \
                                               User.name)
        ['Jane', 'John']

        :param values: rows to insert into the table
        :param returning: selected column of inserted rows to return
        :return: sequence of values of selected column of inserted rows
        """
        stmt = sqlalchemy.insert(cls).returning(returning)
        with cls.session_maker().begin() as session:
            result = session.scalars(stmt, values)
            return result.all()

    @classmethod
    @typing.overload
    def insert(
        cls,
        values: MultiExecuteParams,
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        ...

    @classmethod
    @typing.overload
    def insert(
        cls,
        values: MultiExecuteParams,
        returning: COLUMNS_CLAUSE_ARGUMENT,
    ) -> collections.abc.Sequence[typing.Any]:
        ...

    @classmethod
    @typing.overload
    def insert(
        cls,
        values: SingleExecuteParams,
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> sqlalchemy.Row:
        ...

    @classmethod
    @typing.overload
    def insert(
        cls,
        values: SingleExecuteParams,
        returning: COLUMNS_CLAUSE_ARGUMENT,
    ) -> typing.Any:
        ...

    @classmethod
    @typing.overload
    def insert(
        cls,
        values: AnyExecuteParams,
        returning: None = None,
    ) -> None:
        ...

    @classmethod
    def insert(
        cls,
        values: AnyExecuteParams,
        returning: typing.Union[
            collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
            COLUMNS_CLAUSE_ARGUMENT,
            None,
        ] = None,
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row],
        collections.abc.Sequence[typing.Any],
        sqlalchemy.Row,
        typing.Any,
        None,
    ]:
        """
        Insert one or multiple rows into a table. Columns of inserted rows can be
            selected.

        insert a row into a table without returning anything:

        >>> User.insert({'name': 'Jane'})
        >>> User.insert([{'name': 'Jane'}, {'name': 'John'}])

        insert a row into a table and return a single row of selected columns:

        >>> User.insert({'name': 'Jane'}, [User.id])
        (1,)
        >>> User.insert({'name': 'Jane'}, [User.id, User.name])
        (1, 'Jane')

        insert rows into a table and return a sequence of rows of selected columns:

        >>> User.insert([{'name': 'Jane'}, {'name': 'John'}], [User.id])
        [(1,), (2,)]
        >>> User.insert([{'name': 'Jane'}, {'name': 'John'}], [User.id, User.name])
        [(1, 'Jane'), (2, 'John')]

        insert a row into a table and return the value of a single selected column:

        >>> User.insert({'name': 'Jane'}, User.id)
        1
        >>> User.insert({'name': 'Jane'}, User.name)
        'Jane'

        insert rows into a table and return a sequence of values of a single selected
            column:

        >>> User.insert([{'name': 'Jane'}, {'name': 'John'}], User.id)
        [1, 2]
        >>> User.insert([{'name': 'Jane'}, {'name': 'John'}], User.name)
        ['Jane', 'John']

        :param values: row or seqence of rows to insert into the table
        :param returning: column or sequence of columns of inserted rows to return.
            Cannot be empty.
        :return: selected columns returned from inserted rows.
        """
        # fmt: off
        if isinstance(returning, collections.abc.Sequence) and len(returning) == 0:
            raise ValueError("returning must be a non-empty sequence")

        if isinstance(values, collections.abc.Sequence) \
                and isinstance(returning, collections.abc.Sequence):
            return cls._many_insert_returning_result(values, returning)

        if isinstance(values, collections.abc.Mapping) \
                and isinstance(returning, collections.abc.Sequence):
            return cls._one_insert_returning_result(values, returning)

        if isinstance(values, collections.abc.Sequence) \
                and isinstance(returning, COLUMNS_CLAUSE_ARGUMENT):
            return cls._many_insert_returning_scalar(values, returning)

        if isinstance(values, collections.abc.Mapping) \
                and isinstance(returning, COLUMNS_CLAUSE_ARGUMENT):
            return cls._one_insert_returning_scalar(values, returning)

        return cls._insert_no_returning(values)
        # fmt: on


class Update(SessionMakerMixin):
    @classmethod
    def _update_no_returning(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        values: SingleExecuteParams,
    ) -> None:
        stmt = sqlalchemy.update(cls).where(*where)
        with cls.session_maker().begin() as session:
            session.execute(stmt, values)

    @classmethod
    def _update_returning_result(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        values: SingleExecuteParams,
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        stmt = sqlalchemy.update(cls).where(*where).returning(*returning)
        with cls.session_maker().begin() as session:
            result = session.execute(stmt, values)
            return result.all()

    @classmethod
    def _update_returning_scalar(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        values: SingleExecuteParams,
        returning: COLUMNS_CLAUSE_ARGUMENT,
    ) -> collections.abc.Sequence[typing.Any]:
        stmt = sqlalchemy.update(cls).where(*where).returning(returning)
        with cls.session_maker().begin() as session:
            result = session.scalars(stmt, values)
            return result.all()

    @classmethod
    @typing.overload
    def update(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        values: SingleExecuteParams,
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row],
        collections.abc.Sequence[typing.Any],
    ]:
        ...

    @classmethod
    @typing.overload
    def update(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        values: SingleExecuteParams,
        returning: None,
    ) -> None:
        ...

    @classmethod
    def update(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        values: SingleExecuteParams,
        returning: typing.Union[
            collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
            COLUMNS_CLAUSE_ARGUMENT,
            None,
        ] = None,
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row],
        collections.abc.Sequence[typing.Any],
        None,
    ]:
        if isinstance(returning, collections.abc.Sequence) and len(returning) == 0:
            raise ValueError("returning must be a non-empty sequence")
        if isinstance(returning, collections.abc.Sequence):
            return cls._update_returning_result(where, values, returning)
        if isinstance(returning, COLUMNS_CLAUSE_ARGUMENT):
            return cls._update_returning_scalar(where, values, returning)
        return cls._update_no_returning(where, values)


class Delete(SessionMakerMixin):
    @classmethod
    def _delete_no_returning(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
    ) -> None:
        stmt = sqlalchemy.delete(cls).where(*where)
        with cls.session_maker().begin() as session:
            session.execute(stmt)

    @classmethod
    def _delete_returning_result(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> collections.abc.Sequence[sqlalchemy.Row]:
        stmt = sqlalchemy.delete(cls).where(*where).returning(*returning)
        with cls.session_maker().begin() as session:
            return session.execute(stmt).all()

    @classmethod
    def _delete_returning_scalar(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        returning: COLUMNS_CLAUSE_ARGUMENT,
    ) -> collections.abc.Sequence[typing.Any]:
        stmt = sqlalchemy.delete(cls).where(*where).returning(*returning)
        with cls.session_maker().begin() as session:
            return session.scalars(stmt).all()

    @classmethod
    @typing.overload
    def delete(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        returning: collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row], collections.abc.Sequence[typing.Any]
    ]:
        ...

    @classmethod
    @typing.overload
    def delete(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        returning: None,
    ) -> None:
        ...

    @classmethod
    def delete(
        cls,
        where: collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[bool]],
        returning: typing.Union[
            collections.abc.Sequence[COLUMNS_CLAUSE_ARGUMENT],
            COLUMNS_CLAUSE_ARGUMENT,
            None,
        ] = None,
    ) -> typing.Union[
        collections.abc.Sequence[sqlalchemy.Row],
        collections.abc.Sequence[typing.Any],
        None,
    ]:
        """
        :param where: filters affected row, send empty sequence to affect all rows
            explicitly
        :param returning: select returned columns, leave empty or send empty sequence
            for no return values, if only one value is provided, result will be scalar
        :raises ValueError: if returning is an empty sequence
        """
        if isinstance(returning, collections.abc.Sequence) and len(returning) == 0:
            raise ValueError("returning must be a non-empty sequence")
        if isinstance(returning, collections.abc.Sequence):
            return cls._delete_returning_result(where, returning)
        if isinstance(returning, COLUMNS_CLAUSE_ARGUMENT):
            return cls._delete_returning_scalar(where, returning)
        return cls._delete_no_returning(where)


class DML(Select, Insert, Update, Delete):
    """
    helper class that package all dml method implementations select, insert, update
        and delete
    """
