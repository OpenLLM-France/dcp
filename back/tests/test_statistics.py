"""Tests for statistics and counting methods."""
import pytest
from app.models import Prompt


class TestCountMethods:
    """Tests for count methods."""

    def test_count_prompts_for_task(self, db_session, platform, seeded_task, seeded_prompts):
        """Test counting prompts for a task."""
        task_id = seeded_task['task_id']
        count = platform.count_prompts_for_task(db_session, task_id)
        assert count == 5

    def test_count_prompts_for_task_empty(self, db_session, platform, seeded_instruction):
        """Test counting prompts for task with none."""
        task_id = platform.add_task(db_session, "Empty Task", True, {}, seeded_instruction.id)
        
        count = platform.count_prompts_for_task(db_session, task_id)
        assert count == 0

    def test_count_prompts_for_task_with_generations(self, db_session, platform, seeded_task, seeded_prompts, seeded_generations):
        """Test counting prompts when generations exist."""
        task_id = seeded_task['task_id']
        count = platform.count_prompts_for_task(db_session, task_id)
        assert count == 5

    def test_count_prompts_done_for_user(self, db_session, platform, task_instance_with_vote):
        """Test counting prompts done for a user."""
        user_id = task_instance_with_vote['user_id']
        
        count = platform.count_prompts_done_for_user(db_session, user_id)
        assert count >= 1

    def test_count_prompts_done_for_user_and_task(self, db_session, platform, task_instance_with_vote):
        """Test counting prompts done for user and specific task."""
        user_id = task_instance_with_vote['user_id']
        task_id = task_instance_with_vote['task_id']
        
        count = platform.count_prompts_done_for_user_and_task(db_session, user_id, task_id)
        assert count >= 1


class TestStatMethods:
    """Tests for statistics methods."""

    def test_get_stat_user_task(self, db_session, platform, task_instance_with_vote):
        """Test getting user task statistics."""
        stats = platform.get_stat_user_task(db_session)
        
        assert stats is not None
        assert isinstance(stats, list)
        if len(stats) > 0:
            assert 'user_id' in stats[0]
            assert 'task_id' in stats[0]
            assert 'count' in stats[0]

    def test_get_stat_user_task_empty(self, db_session, platform):
        """Test getting user task statistics with no data."""
        stats = platform.get_stat_user_task(db_session)
        
        assert stats == []

    def test_get_tasks_done_for_user(self, db_session, platform, task_instance_with_vote):
        """Test getting tasks done for a user."""
        user_id = task_instance_with_vote['user_id']
        
        tasks = platform.get_tasks_done_for_user(db_session, user_id)
        
        assert tasks is not None
        assert isinstance(tasks, list)
        if len(tasks) > 0:
            assert 'task_id' in tasks[0]
            assert 'count' in tasks[0]

    def test_get_tasks_done_for_user_empty(self, db_session, platform, test_user):
        """Test getting tasks done for user with no tasks."""
        user_id = test_user['user_id']
        
        tasks = platform.get_tasks_done_for_user(db_session, user_id)
        
        assert tasks == []

    def test_get_tasks_done(self, db_session, platform, task_instance_with_vote):
        """Test getting users who completed a task."""
        task_id = task_instance_with_vote['task_id']
        
        users = platform.get_tasks_done(db_session, task_id)
        
        assert users is not None
        assert isinstance(users, list)
        if len(users) > 0:
            assert 'user_id' in users[0]
            assert 'count' in users[0]

    def test_get_tasks_done_empty(self, db_session, platform, seeded_task):
        """Test getting users for task with no completions."""
        task_id = seeded_task['task_id']
        
        users = platform.get_tasks_done(db_session, task_id)
        
        assert users == []

    def test_get_total_votes(self, db_session, platform, task_instance_with_vote):
        """Test getting total votes."""
        total = platform.get_total_votes(db_session)
        assert total == 1

    def test_get_total_votes_empty(self, db_session, platform):
        """Test getting total votes with no votes."""
        total = platform.get_total_votes(db_session)
        assert total == 0

    def test_get_tasks_done_for_user_and_task(self, db_session, platform, task_instance_with_vote):
        """Test getting tasks done for user and specific task."""
        user_id = task_instance_with_vote['user_id']
        task_id = task_instance_with_vote['task_id']
        
        result = platform.get_tasks_done_for_user_and_task(db_session, user_id, task_id)
        
        assert result is not None
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'user_id' in result[0]
            assert 'task_id' in result[0]
            assert 'count' in result[0]

    def test_get_tasks_done_for_user_and_task_empty(self, db_session, platform, test_user, seeded_task):
        """Test getting tasks done for user and task with no data."""
        user_id = test_user['user_id']
        task_id = seeded_task['task_id']
        
        result = platform.get_tasks_done_for_user_and_task(db_session, user_id, task_id)
        
        assert result == []


class TestVotesSince:
    """Tests for get_votes_since method."""

    def test_get_votes_since_returns_votes(self, db_session, platform, seeded_instruction):
        """Test that get_votes_since returns votes since a timestamp."""
        from datetime import datetime, timedelta
        
        task_id = platform.add_task(
            db_session, 
            "Test Task", 
            True, 
            {}, 
            seeded_instruction.id
        )
        
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)
        
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)
        
        task_instance = platform.get_task_instance_for_user(
            db_session, 
            str(task_id), 
            user_id
        )
        
        before_timestamp = datetime.now() - timedelta(seconds=1)
        
        platform.add_vote(
            db_session,
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        votes = platform.get_votes_since(
            db_session, 
            before_timestamp, 
            0
        )
        
        assert len(votes) >= 1
        vote = votes[0]
        assert 'id' in vote
        assert 'taskinstance_id' in vote
        assert 'user_id' in vote
        assert 'prompt_id' in vote
        assert 'answer' in vote
        assert 'timestamp' in vote
        assert 'type' in vote
        assert vote['type'] == 'vote'

    def test_get_votes_since_with_last_vote_id(self, db_session, platform, seeded_instruction):
        """Test that get_votes_since filters by last_vote_id."""
        from datetime import datetime, timedelta
        
        task_id = platform.add_task(
            db_session, 
            "Test Task", 
            True, 
            {}, 
            seeded_instruction.id
        )
        
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)
        
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)
        
        task_instance = platform.get_task_instance_for_user(
            db_session, 
            str(task_id), 
            user_id
        )
        
        before_timestamp = datetime.now() - timedelta(seconds=1)
        
        platform.add_vote(
            db_session,
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        votes = platform.get_votes_since(
            db_session, 
            before_timestamp, 
            999999
        )
        
        assert votes == []

    def test_get_votes_since_empty(self, db_session, platform, seeded_instruction):
        """Test that get_votes_since returns empty list when no votes exist."""
        from datetime import datetime, timedelta
        
        task_id = platform.add_task(
            db_session, 
            "Test Task", 
            True, 
            {}, 
            seeded_instruction.id
        )
        
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)
        
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)
        
        task_instance = platform.get_task_instance_for_user(
            db_session, 
            str(task_id), 
            user_id
        )
        
        votes = platform.get_votes_since(
            db_session, 
            datetime.now(), 
            0
        )
        
        assert votes == []


@pytest.fixture
def task_instance_with_vote(db_session, platform, seeded_instruction):
    """Simple setup with a task instance and vote."""
    task_id = platform.add_task(
        db_session, 
        "Test Task", 
        True, 
        {}, 
        seeded_instruction.id
    )
    
    session_id, user_id = platform.add_user(db_session)
    platform.add_usertaskpermission(db_session, user_id, task_id)
    
    prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
    
    params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
    gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
    gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)
    
    task_instance = platform.get_task_instance_for_user(
        db_session, 
        str(task_id), 
        user_id
    )
    
    platform.add_vote(
        db_session,
        task_instance['id'],
        gen_a_id,
        gen_b_id,
        True,
        "quality",
        1
    )
    
    return {
        'task_instance': task_instance,
        'user_id': user_id,
        'task_id': task_id,
        'gen_a_id': gen_a_id,
        'gen_b_id': gen_b_id
    }
