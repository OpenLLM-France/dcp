"""Tests for user management, sessions, and permissions."""
import pytest
import uuid
from app.models import User, UserSession, UserTaskPermission


class TestUserManagement:
    """Tests for user creation and session management."""

    def test_add_user_creates_user_and_session(self, db_session, platform):
        """Test that add_user creates both user and session."""
        session_id, user_id = platform.add_user(db_session)
        
        user = db_session.get(User, user_id)
        assert user is not None
        assert user.login_name_in_use is False
        
        session = db_session.get(UserSession, session_id)
        assert session is not None
        assert session.user_id == user_id

    def test_add_user_generates_unique_user_ids(self, db_session, platform):
        """Test that each user gets a unique ID."""
        _, user_id_1 = platform.add_user(db_session)
        _, user_id_2 = platform.add_user(db_session)
        
        assert user_id_1 != user_id_2

    def test_add_user_generates_unique_session_ids(self, db_session, platform):
        """Test that each session gets a unique UUID."""
        session_id_1, _ = platform.add_user(db_session)
        session_id_2, _ = platform.add_user(db_session)
        
        assert session_id_1 != session_id_2
        assert isinstance(session_id_1, uuid.UUID)
        assert isinstance(session_id_2, uuid.UUID)

    def test_add_usertaskpermission(self, db_session, platform, test_user, seeded_task):
        """Test adding task permission for a user."""
        platform.add_usertaskpermission(db_session, test_user['user_id'], seeded_task['task_id'])
        
        permission = db_session.query(UserTaskPermission).filter(
            UserTaskPermission.user_id == test_user['user_id'],
            UserTaskPermission.task_id == seeded_task['task_id']
        ).one()
        
        assert permission is not None
        assert permission.user_id == test_user['user_id']

    def test_add_usertaskpermission_multiple_tasks(self, db_session, platform, test_user):
        """Test adding permissions for multiple tasks."""
        from app.models import Instruction
        
        instruction_id = platform.add_instruction(db_session, "Instruction 1")
        task_id_1 = platform.add_task(db_session, "Task 1", True, {}, instruction_id)
        task_id_2 = platform.add_task(db_session, "Task 2", True, {}, instruction_id)
        
        platform.add_usertaskpermission(db_session, test_user['user_id'], task_id_1)
        platform.add_usertaskpermission(db_session, test_user['user_id'], task_id_2)
        
        permissions = db_session.query(UserTaskPermission).filter(
            UserTaskPermission.user_id == test_user['user_id']
        ).all()
        
        assert len(permissions) == 2

    def test_get_user_id_success(self, db_session, platform, test_user):
        """Test getting user ID from session."""
        user_id = platform.get_user_id(db_session, test_user['session_id'])
        assert user_id == test_user['user_id']

    def test_get_user_id_failure(self, db_session, platform):
        """Test getting user ID from invalid session."""
        fake_session_id = uuid.uuid4()
        user_id = platform.get_user_id(db_session, fake_session_id)
        assert user_id is None

    def test_get_users(self, db_session, platform, test_user):
        """Test getting all users."""
        users = platform.get_users(db_session)
        assert len(users) >= 1

    def test_get_tasks(self, db_session, platform, seeded_task):
        """Test getting all tasks."""
        tasks = platform.get_tasks(db_session)
        assert len(tasks) >= 1

    def test_get_public_tasks(self, db_session, platform):
        """Test getting public tasks via get_tasks_for_user."""
        from app.models import Instruction
        
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        platform.add_task(db_session, "Public Task", True, {}, instruction_id)
        
        # Create a user to get tasks
        session_id, user_id = platform.add_user(db_session)
        
        tasks = platform.get_tasks_for_user(db_session, user_id)
        assert len(tasks) >= 1
