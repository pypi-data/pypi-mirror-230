from pathlib import Path
from typing import Optional, Tuple
from collections import defaultdict

import appdirs
from sqlalchemy import Engine, create_engine as _create_engine, MetaData

DEFAULT_NAME = "Database.db"

_engineDict = defaultdict(list)


def get_engine(
    app_name: str,
    db_name: str = DEFAULT_NAME,
    metadata: Optional[MetaData] = None,
    **kwargs,
) -> Engine:
    """Return an SQlAlchemy Engine for a specific app"""
    db_path, newDB = _setupDB(app_name, db_name)
    engine = _create_engine(f"sqlite:///{str(db_path)}", **kwargs)

    _engineDict[app_name].append(engine)

    if metadata is not None and newDB:
        metadata.create_all(engine)

    return engine


def _setupDB(app_name: str, db_name: str) -> Tuple[Path, bool]:
    """Setup the database file in the appropriate location.
    If the file already exists, nothing is changed.
    Returns a Path object to the database"""

    db_path = _getDBPath(app_name, db_name)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    freshDB = not db_path.exists()
    db_path.touch(exist_ok=True)
    return db_path, freshDB


def _getDBPath(app_name: str, db_name: str = DEFAULT_NAME) -> Path:
    """Return DB Path, without creating any of the intermediate files/folders."""
    db_dir = Path(appdirs.user_data_dir(appname=app_name))
    db_path = db_dir / db_name
    return db_path


def remove_database(app_name: str, db_name: str = DEFAULT_NAME) -> None:
    """Remove database file.

    Also removes the data folder tree, if it is empty."""

    for engine in _engineDict[app_name]:
        engine.dispose(close=True)

    db_path = _getDBPath(app_name, db_name)
    db_path.unlink(missing_ok=True)
    temp = db_path.parent
    try:
        while temp != temp.parent:
            temp.rmdir()
            temp = temp.parent
    except OSError:
        # Something else is still in the directory.
        # Ignore this, assume someone else put something here.
        pass


if __name__ == "__main__":
    get_engine("MyScractchApp")
