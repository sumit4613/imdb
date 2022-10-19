from typing import Dict, Generator, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import database_exists, create_database

from app import models
from app.api.deps import get_db
from app.db.base_class import Base
from app.tests.utils import (
    get_admin_token_headers,
    get_user_token_headers,
    create_user,
    create_random_movie,
    create_random_movies,
)
from config import settings
from main import app

engine = create_engine(settings.SQLALCHEMY_TEST_DATABASE_URI)
if not database_exists(engine.url):
    create_database(engine.url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db() -> Generator:
    # Set up the database once
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(db) -> Generator:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture(scope="module")
def admin_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return get_admin_token_headers(db=db, client=client)


@pytest.fixture(scope="module")
def user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return get_user_token_headers(db=db, client=client)


@pytest.fixture(scope="module")
def admin_user(db: Session) -> models.User:
    return create_user(db=db, is_admin=True)


@pytest.fixture(scope="module")
def normal_user(db: Session) -> Tuple[models.User, str]:
    return create_user(db=db, is_admin=False)


@pytest.fixture(scope="module")
def disabled_user(db: Session) -> models.User:
    return create_user(db=db, is_admin=False, is_active=False)


@pytest.fixture(scope="module")
def get_movie(db: Session) -> models.Movies:
    return create_random_movie(db=db)


@pytest.fixture(scope="module")
def get_movies(db: Session):
    return create_random_movies(db=db)
