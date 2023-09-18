from typing import Optional

from sqlalchemy import Engine, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

import ezlocaldb as ezdb

appName = "MyAppName"
dbName = "MyTestDatabase.db"


def test_get_engine_and_remove_db():
    engine = ezdb.get_engine(appName)
    assert isinstance(engine, Engine)
    ezdb.remove_database(appName)
    dbPath = ezdb._getDBPath(appName)
    assert not dbPath.exists()


def test_db_path_setup_and_removal():
    dbPath, _ = ezdb._setupDB(appName, dbName)
    assert dbPath.exists()
    ezdb.remove_database(appName, dbName)
    assert not dbPath.exists()


class Base(DeclarativeBase):
    pass


class ObjectTest(Base):
    __tablename__ = "TestingTable"
    id: Mapped[int] = mapped_column(primary_key=True)
    testfield: Mapped[str]
    optfield: Mapped[Optional[str]]


def test_create_wMetadata_and_delete():
    """Test Database creationg with metadata emission, then DB removal"""
    # Test only works if database doesn't exist ahead of time.
    ezdb.remove_database(appName, dbName)
    dbPath = ezdb._getDBPath(appName, dbName)
    assert not dbPath.exists()

    eng = ezdb.get_engine("MyTestDatabase.db", metadata=Base.metadata)
    newMetadata = MetaData()
    newMetadata.reflect(bind=eng)
    assert "TestingTable" in newMetadata.tables
    testingTable = newMetadata.tables["TestingTable"]
    assert "id" in testingTable.c

    ezdb.remove_database(appName, dbName)

    assert not dbPath.exists()

    # Try using disposed engine and see what happens!
    newMetadata.create_all(eng)
    assert not dbPath.exists()


def test_CRUD_and_multiple_engines():
    ezdb.remove_database(appName)
    eng1 = ezdb.get_engine(appName, metadata=Base.metadata)
    eng2 = ezdb.get_engine(appName, metadata=Base.metadata)

    with Session(eng1) as ses:
        t1 = ObjectTest(testfield="hello")
        ses.add(t1)
        ses.commit()

    with Session(eng2) as ses:
        t2 = ses.query(ObjectTest).scalar()
        assert t2.testfield == "hello"
        ses.delete(t2)
        ses.commit()

    with Session(eng1) as ses:
        assert ses.query(ObjectTest).scalar() is None

    ezdb.remove_database(appName)
