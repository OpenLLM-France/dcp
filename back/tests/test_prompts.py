"""Tests for prompt management."""
import pytest
from app.models import Prompt, Task


class TestPromptCreation:
    """Tests for prompt creation."""

    def test_add_prompt_creates_prompt(self, db_session, platform, seeded_task):
        """Test that add_prompt creates a prompt."""
        task_id = seeded_task['task_id']
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt text")
        
        assert prompt_id is not None
        prompt = db_session.get(Prompt, prompt_id)
        assert prompt is not None
        assert prompt.text == "Test prompt text"
        assert prompt.task_id == task_id

    def test_add_prompt_generates_uuid(self, db_session, platform, seeded_task):
        """Test that add_prompt generates a UUID."""
        task_id = seeded_task['task_id']
        prompt_id = platform.add_prompt(db_session, task_id, "Prompt")
        
        # Should be a UUID (string or UUID object)
        import uuid
        assert prompt_id is not None
        uuid.UUID(str(prompt_id))

    def test_add_multiple_prompts_for_task(self, db_session, platform, seeded_task):
        """Test adding multiple prompts to same task."""
        task_id = seeded_task['task_id']
        prompt_ids = []
        for i in range(5):
            prompt_id = platform.add_prompt(db_session, task_id, f"Prompt {i}")
            prompt_ids.append(prompt_id)
        
        prompts = db_session.query(Prompt).filter(Prompt.task_id == task_id).all()
        assert len(prompts) == 5
        assert len(set(prompt_ids)) == 5


class TestPromptRetrieval:
    """Tests for retrieving prompts."""

    def test_get_prompts(self, db_session, platform, seeded_prompts):
        """Test getting all prompts."""
        prompts = platform.get_prompts(db_session)
        assert len(prompts) == 5

    def test_get_prompts_for_task(self, db_session, platform, seeded_task, seeded_prompts):
        """Test getting all prompts for a task."""
        task_id = seeded_task['task_id']
        prompts = platform.get_prompts_for_task(db_session, task_id)
        
        assert len(prompts) == 5
        assert all(p['text'] is not None for p in prompts)

    def test_get_prompts_for_task_empty(self, db_session, platform):
        """Test getting prompts for task with no prompts."""
        from app.models import Instruction
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Empty Task", True, {}, instruction_id)
        
        prompts = platform.get_prompts_for_task(db_session, task_id)
        assert len(prompts) == 0

    def test_find_prompt_exists(self, db_session, platform, seeded_task):
        """Test finding a prompt that exists."""
        task_id = seeded_task['task_id']
        platform.add_prompt(db_session, task_id, "Find me")
        
        result = platform.find_prompt(db_session, task_id, "Find me")
        
        assert result is not None
        assert result['text'] == "Find me"

    def test_find_prompt_not_exists(self, db_session, platform, seeded_task):
        """Test finding a prompt that doesn't exist."""
        task_id = seeded_task['task_id']
        result = platform.find_prompt(db_session, task_id, "Non Existent")
        
        assert result is None


class TestPromptStats:
    """Tests for prompt statistics."""

    def test_count_prompts_for_task(self, db_session, platform, seeded_task, seeded_prompts):
        """Test counting prompts for a task."""
        task_id = seeded_task['task_id']
        count = platform.count_prompts_for_task(db_session, task_id)
        assert count == 5

    def test_count_prompts_for_task_empty(self, db_session, platform):
        """Test counting prompts for task with none."""
        from app.models import Instruction
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Empty Task", True, {}, instruction_id)
        
        count = platform.count_prompts_for_task(db_session, task_id)
        assert count == 0
