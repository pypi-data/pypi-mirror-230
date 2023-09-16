# Model DML

[![Latest Release](https://lab.frogg.it/dorianturba/model_dml/-/badges/release.svg?order_by=release_at)](https://lab.frogg.it/dorianturba/model_dml/-/releases)
[![Pipeline](https://lab.frogg.it/dorianturba/model_dml/badges/main/pipeline.svg)](https://lab.frogg.it/dorianturba/model_dml/-/pipelines)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/model_dml.svg)](https://pypi.org/project/model_dml)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/model_dml)](https://pypi.org/project/model_dml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://lab.frogg.it/dorianturba/model_dml/-/blob/main/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Open-Source/Open-to-Contribution](https://img.shields.io/badge/%20OpenSource-OpenToContribution-%231674b1?style=flat&labelColor=yellow)](https://opensource.guide/how-to-contribute/)
[![Mattermost-model_dml](https://img.shields.io/badge/Mattermost-ModelDML-%2379eb00?style=flat&logo=mattermost)](https://chat.froggit.fr/signup_user_complete/?id=e6r8p645fbbut8wubbdph9ot9w&sbr=su)

Extends your SQLAlchemy models with DML mixins.

<!-- TOC -->

* [Model DML](#model-dml)
  * [Features](#features)
  * [How to grow with model_dml](#how-to-grow-with-modeldml)
    * [Why not use model_dml](#why-not-use-modeldml)
    * [How not to use model_dml](#how-not-to-use-modeldml)
    * [What kind of change may be needed](#what-kind-of-change-may-be-needed)
  * [Get model_dml for your project](#get-modeldml-for-your-project)
    * [Requirements](#requirements)
    * [Installation](#installation)
  * [Use model_dml in your project](#use-modeldml-in-your-project)
    * [Modify your sqlalchemy Base](#modify-your-sqlalchemy-base)
    * [Compose your model with what you need](#compose-your-model-with-what-you-need)
    * [Use the DML methods](#use-the-dml-methods)

<!-- TOC -->

## Features

* Four methods for [DML][DML] operations: `select`, `insert`, `update`, `delete`.
* Add those methods to models through mixin classes.
* Support returning selected columns for all methods.

## How to grow with model_dml

### Why not use model_dml

* No typed return values. It is theoretically possible to add annotation that will infer
  the return type of the methods such as select(id, name) would return a namedtuple with
  id as `int` and name as `str`. If you want to add this feature, you should read the
  method code and implement it yourself. Without `model_dml` abstraction, the type
  inference works better.

### How not to use model_dml

This package is not meant to be used systematically as an installed package. You may
want to copy a specific function that you need in your project instead of installing the
whole package.

### What kind of change may be needed

Let's take the `select` method. It is implemented to return a sequence of rows. If you
want to order the rows by a column, you need to change the SQL statement construction.

1. Find the source code of select method returning rows

    ```python
    def _select_result(cls, where, columns, limit):
        stmt = sqlalchemy.select(*columns).where(*where).limit(limit)
        with cls.session_maker().begin() as session:
            return session.execute(stmt).all()
    ```

2. Copy implementation in your code

    ```python
    # Your code
    stmt = sqlalchemy.select(*columns).where(*where).limit(limit)
    with cls.session_maker().begin() as session:
        return session.execute(stmt).all()
    # Your code
    ```

3. Update implementation accordingly to your needs

   > ! Here session_maker should be the session factory of your project. Please
   see [session_basics - using a sessionmaker][using-a-sessionmaker].

    ```python
    # Your code
    stmt = sqlalchemy.select(User.id, User.name).limit(10).order_by(User.name)
    with session_maker().begin() as session: 
        results = session.execute(stmt).all()
    # Your code
    ```

   Bravo :D

## Get model_dml for your project

### Requirements

* Python 3.8+

### Installation

```bash
pip install model_dml
```

## Use model_dml in your project

### Modify your sqlalchemy Base

To use `model_dml`, you need to create a custom base class for your models with
a `session_maker` method.

What is a sessionmaker:

* [Using a sessionmaker][Using a sessionmaker]
* [sessionmaker documentation and example][sessionmaker documentation and example]

```python
class Base(sqlalchemy.orm.DeclarativeBase):
    @classmethod
    def session_maker(cls) -> sqlalchemy.orm.sessionmaker:
        return < Namespace >.Session
```

This method exist to allow DML methods to access the `sessionmaker` without creating a
new reference
that would also need to be monkey patched. By returning the `sessionmaker` from the
namespace, only
`<Namespace>.Session` needs to be monkey patched.

### Compose your model with what you need

```python
class User(base, model_dml.Insert, model_dml.Update, model_dml.Delete):
    __tablename__ = "users"
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(30))
```

You can use `model_dml.DML` which is a helper class that composes all the mixins
together.

```python
class User(base, model_dml.DML):
    __tablename__ = "users"
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(primary_key=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(30))
```

### Use the DML methods

```python
User.insert(dict(name="John"))
User.insert({'name': "Jane"})
user = User.insert({'name': "Jack"}, returning=[User.id, User.name])
```

[DML]: https://en.wikipedia.org/wiki/Data_manipulation_language#SQL

[using-a-sessionmaker]: https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker

[Using a sessionmaker]: https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker

[sessionmaker documentation and example]: https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.sessionmaker
