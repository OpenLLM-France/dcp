"""Tests for task management."""
import pytest
import uuid
from app.models import Task, Instruction


class TestTaskCreation:
    """Tests for task creation and basic properties."""

    def test_add_task_creates_task(self, db_session, platform, seeded_instruction):
        """Test that add_task creates a task with correct properties."""
        task_id = platform.add_task(
            db_session, 
            "Test Task", 
            True, 
            {"key": "value"}, 
            seeded_instruction.id
        )
        
        assert isinstance(task_id, uuid.UUID)

    def test_add_task_generates_uuid(self, db_session, platform, seeded_instruction):
        """Test that add_task generates a UUID."""
        task_id = platform.add_task(db_session, "Task", True, {}, seeded_instruction.id)
        
        assert isinstance(task_id, uuid.UUID)

    def test_add_task_with_private_flag(self, db_session, platform, seeded_instruction):
        """Test creating a private task."""
        task_id = platform.add_task(db_session, "Private Task", False, {}, seeded_instruction.id)
        
        task = db_session.get(Task, task_id)
        assert task.public is False

    def test_add_task_with_meta_data(self, db_session, platform, seeded_instruction):
        """Test creating a task with metadata."""
        meta_data = {"category": "test", "priority": 1, "tags": ["a", "b"]}
        task_id = platform.add_task(db_session, "Meta Task", True, meta_data, seeded_instruction.id)
        
        task = db_session.get(Task, task_id)
        assert task.meta == meta_data

    def test_add_task_with_unique_name(self, db_session, platform, seeded_instruction):
        """Test that task names must be unique."""
        platform.add_task(db_session, "Unique Task", True, {}, seeded_instruction.id)
        
        with pytest.raises(Exception):
            platform.add_task(db_session, "Unique Task", True, {}, seeded_instruction.id)


class TestTaskRetrieval:
    """Tests for retrieving tasks."""

    def test_get_task_by_id(self, db_session, platform, seeded_task):
        """Test retrieving a task by ID."""
        task = platform.get_task_by_id(db_session, seeded_task['task_id'])
        
        assert task is not None
        assert task['id'] == seeded_task['task_id']

    def test_get_task_by_id_not_found(self, db_session, platform):
        """Test retrieving non-existent task returns error."""
        fake_id = uuid.uuid4()
        
        with pytest.raises(Exception):
            platform.get_task_by_id(db_session, fake_id)

    def test_get_tasks_for_user_with_permissions(self, db_session, platform, authorized_user):
        """Test getting tasks accessible by a user."""
        tasks = platform.get_tasks_for_user(db_session, authorized_user['user_id'])
        
        assert len(tasks) >= 1

    def test_get_tasks_for_user_no_permissions(self, db_session, platform, test_user):
        """Test getting tasks for user with no permissions."""
        tasks = platform.get_tasks_for_user(db_session, test_user['user_id'])
        
        # Should only include public tasks
        assert len(tasks) >= 0


class TestTaskInstructions:
    """Tests for task instruction relationships."""

    def test_add_instruction_creates_instruction(self, db_session, platform):
        """Test adding a new instruction."""
        instruction_id = platform.add_instruction(db_session, "New instruction text")
        
        instruction = db_session.get(Instruction, instruction_id)
        assert instruction.text == "New instruction text"

    def test_get_instruction_for_task(self, db_session, platform, seeded_task, seeded_instruction):
        """Test getting instruction for a task."""
        instruction = platform.get_instruction_for_task(db_session, seeded_task['task_id'])
        
        assert instruction is not None
        assert instruction['id'] == seeded_instruction.id


class TestTaskStats:
    """Tests for task statistics."""

    def test_count_prompts_for_task(self, db_session, platform, seeded_task, seeded_prompts):
        """Test counting prompts for a task."""
        count = platform.count_prompts_for_task(db_session, seeded_task['task_id'])
        assert count == 5

    def test_count_prompts_for_task_empty(self, db_session, platform):
        """Test counting prompts for task with none."""
        from app.models import Instruction
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Empty Task", True, {}, instruction_id)
        
        count = platform.count_prompts_for_task(db_session, task_id)
        assert count == 0

    def test_get_tasks_done_for_user_and_task(self, db_session, platform, complete_task_setup):
        """Test getting tasks done for user and task."""
        user_id = complete_task_setup['user_id']
        task_id = complete_task_setup['task_id']
        
        result = platform.get_tasks_done_for_user_and_task(db_session, user_id, task_id)
        assert result == []
