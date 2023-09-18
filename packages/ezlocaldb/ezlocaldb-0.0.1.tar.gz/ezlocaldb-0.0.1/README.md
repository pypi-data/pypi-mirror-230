# ezlocaldb

Version 0.0.1

Easy, local databases for no-sweat persistence. This convinience package wraps
small parts of `appdirs`, `sqlite3`, and `sqlalchemy`, to easily create
databases for local applications. The package saves about 15 lines of code, but
it's 15 lines I find myself writting at the start of many projects, so maybe it
will save you some time too.

## Installation

### PIP
The easiest way to install `ezlocaldb` is with pip
```bash
  pip install ezlocaldb
```

## Usage/Examples

### Quick Start
To work with `sqlalchemy` use `get_engine` to get an `engine` object for
database access. The first argument to `get_engine` is the name of your
application, which is used to uniquely specify the database.

```python
from ezlocaldb import get_engine
from sqlalchemy import Session

# Get an sqlalchemy engine to use with sqlalchemy.Session
engine = get_engine(app_name="MyAmazingApp")

with Session(engine) as session:
    # Now work with session to initalize database,
    # or execute other CRUD operations.
    pass
```

When you call `get_engine`, ezlocaldb checks to see if your database was created
previously. If it wasn't it creates a new `sqlite` database. Either way, it
returns an `engine` which can be used to access the database.

### Removing or refreshing databases
If you want to remove or refresh the database, use

```python
from ezlocaldb import remove_database, get_engine

remove_database("MyAmazingApp")

# To recreate the database (with no data in it) use
engine = get_engine("MyAmazingApp")
```

### Initializing the Schema
Usually, getting tables and such setup is just a little tricky. When should you
emit `CREATE TABLE` commands? Is everything in place? Did you just overwrite
your data?

With `ezlocaldb` you can pass a `sqlalchemy.MetaData` instance as a keyword
argument to `get_engine`. If you're using the ORM, it's as simple as this:

```python
from sqlalchemy.orm import DeclarativeBase
from ezlocaldb import get_engine

class Base(DeclarativeBase):
   pass

# More ORM classes derived from Base
# ...

engine = get_engine('MyAmazingApp',metadata=Base.metadata)
```

If your database file hasn't been created, `get_engine` will `create_all` the
tables, etc. represented in your ORM tree. If the file was previously created,
the metadata argument is ignored. This way you can quickly get a database setup
for orm operations, and not worry about accidentally overwritting all your data.

If you make changes to your ORM structure, you can use `remove_database` from a
repl or other function, and call `get_engine` with the `metadata` argument again,
and the new database will reflect all your new structure.

> **A note on migrations**.
> Database migrations are a complicated subject. If you want to keep your data
> while you revise your ORM structure or Database Schema, you're probably ready
> to graduate to using full `SQLAlchemy`, and look at `Alembic`.

### Thank You!
