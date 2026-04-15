import uuid
import pytest
from fastapi import HTTPException

from app.models import User, UserSession
from app.service import DataCollectionPlatform


def test_add_user_creates_user_and_session(db_session, platform):
    """`add_user` should insert a User and a UserSession and return their IDs."""
    session_id, user_id = platform.add_user(db_session)

    # returned IDs are UUID for session, int for user
    assert isinstance(session_id, uuid.UUID)
    assert isinstance(user_id, int)

    # verify rows exist in DB
    db_user = db_session.query(User).filter_by(id=user_id).one()
    db_session_row = (
        db_session.query(UserSession)
        .filter_by(id=session_id, user_id=user_id)
        .one()
    )
    assert db_user.id == user_id
    assert db_session_row.id == session_id
    assert db_session_row.user_id == user_id


def test_get_user_id_success_and_failure(db_session, platform):
    """`get_user_id` returns user id for a valid session; returns None for unknown/invalid."""
    # create a user & session
    session_id, user_id = platform.add_user(db_session)

    # success path
    got_user_id = platform.get_user_id(db_session, session_id)
    assert got_user_id == user_id

    # unknown session returns None
    missing = platform.get_user_id(db_session, uuid.uuid4())
    assert missing is None
