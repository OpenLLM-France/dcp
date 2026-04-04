"""Tests for retrieval methods."""
import pytest
from datetime import datetime, timedelta
from app.models import TaskInstance, Vote, Tag, Prompt


@pytest.fixture
def votes_setup(db_session, platform, seeded_task):
    """Create a task instance with votes for retrieval tests."""
    from app.models import TaskInstance, UserSession
    from datetime import datetime
    
    session_id, user_id = platform.add_user(db_session)
    platform.add_usertaskpermission(db_session, user_id, seeded_task['task_id'])
    
    # Create prompt and generations directly
    prompt = db_session.query(Prompt).filter_by(task_id=seeded_task['task_id']).first()
    if not prompt:
        prompt_id = platform.add_prompt(db_session, seeded_task['task_id'], "Test prompt for votes")
        prompt = db_session.query(Prompt).filter_by(id=prompt_id).first()
    
    params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
    gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt.id)
    gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt.id)
    
    # Create task instance directly
    db_task_instance = TaskInstance(
        user_id=user_id,
        prompt_id=prompt.id,
        generation_a_id=gen_a_id,
        generation_b_id=gen_b_id
    )
    db_session.add(db_task_instance)
    db_session.commit()
    db_session.refresh(db_task_instance)
    task_instance_id = db_task_instance.id
    
    vote1 = platform.add_vote(
        db_session, task_instance_id, gen_a_id, gen_b_id,
        True, "quality", 1
    )
    vote2 = platform.add_vote(
        db_session, task_instance_id, gen_a_id, gen_b_id,
        False, "quality", 0
    )
    
    tag1 = platform.add_tag(
        db_session, task_instance_id, gen_a_id,
        True, "good"
    )
    tag2 = platform.add_tag(
        db_session, task_instance_id, gen_b_id,
        False, "bad"
    )
    
    return {
        'task_instance_id': task_instance_id,
        'user_id': user_id,
        'gen_a_id': gen_a_id,
        'gen_b_id': gen_b_id,
        'vote1': vote1,
        'vote2': vote2,
        'tag1': tag1,
        'tag2': tag2
    }


class TestTaskInstanceRetrieval:
    """Tests for get_task_instances_for_prompt method."""

    def test_get_task_instances_for_prompt_creates_instance(self, db_session, platform, seeded_task):
        """Test that get_task_instance_for_user creates task instances."""
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, seeded_task['task_id'])
        
        prompt_id = platform.add_prompt(db_session, seeded_task['task_id'], "Test prompt")
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
        
        task_instance = platform.get_task_instance_for_user(
            db_session, str(seeded_task['task_id']), user_id
        )
        
        assert task_instance is not None
        assert 'id' in task_instance
        assert 'prompt' in task_instance
        assert 'generations' in task_instance

    def test_get_task_instances_for_prompt_multiple(self, db_session, platform, seeded_task):
        """Test getting task instances for a prompt with multiple users."""
        prompt_id = platform.add_prompt(db_session, seeded_task['task_id'], "Test prompt")
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
        
        user_ids = []
        for i in range(3):
            session_id, user_id = platform.add_user(db_session)
            platform.add_usertaskpermission(db_session, user_id, seeded_task['task_id'])
            platform.get_task_instance_for_user(db_session, str(seeded_task['task_id']), user_id)
            user_ids.append(user_id)
        
        task_instances = platform.get_task_instances_for_prompt(db_session, prompt_id)
        
        assert len(task_instances) == 3
        for ti in task_instances:
            assert 'id' in ti
            assert 'user_id' in ti
            assert 'generation_a_id' in ti
            assert 'generation_b_id' in ti
            assert 'timestamp' in ti

    def test_get_task_instances_for_prompt_empty(self, db_session, platform, seeded_task):
        """Test getting task instances for a prompt with no instances."""
        prompt_id = platform.add_prompt(db_session, seeded_task['task_id'], "Test prompt")
        
        task_instances = platform.get_task_instances_for_prompt(db_session, prompt_id)
        
        assert task_instances == []


class TestVotesRetrieval:
    """Tests for get_votes_since method."""

    def test_get_votes_since_returns_votes(self, db_session, platform, votes_setup):
        """Test getting votes since a timestamp."""
        votes = platform.get_votes_since(db_session, datetime.min, 0)
        
        assert len(votes) >= 2
        vote = votes[0]
        assert 'id' in vote
        assert 'taskinstance_id' in vote
        assert 'user_id' in vote
        assert 'prompt_id' in vote
        assert 'answer' in vote
        assert 'timestamp' in vote
        assert vote['type'] == 'vote'

    def test_get_votes_since_filters_by_timestamp(self, db_session, platform, votes_setup):
        """Test that get_votes_since filters by timestamp."""
        votes = platform.get_votes_since(db_session, datetime.max, 0)
        
        assert len(votes) == 0

    def test_get_votes_since_filters_by_id(self, db_session, platform, votes_setup):
        """Test that get_votes_since filters by vote ID."""
        votes = platform.get_votes_since(db_session, datetime.min, votes_setup['vote2'].id)
        
        assert len(votes) == 0

    def test_get_votes_since_multiple_votes(self, db_session, platform, votes_setup):
        """Test getting multiple votes since a point."""
        votes = platform.get_votes_since(db_session, datetime.min, votes_setup['vote1'].id)
        
        assert len(votes) == 1
        assert votes[0]['id'] == votes_setup['vote2'].id
        assert votes[0]['answer'] == 0


class TestTagsRetrieval:
    """Tests for get_tags_since method."""

    def test_get_tags_since_returns_tags(self, db_session, platform, votes_setup):
        """Test getting tags since a timestamp."""
        tags = platform.get_tags_since(db_session, datetime.min, 0)
        
        assert len(tags) >= 2
        tag = tags[0]
        assert 'id' in tag
        assert 'taskinstance_id' in tag
        assert 'user_id' in tag
        assert 'prompt_id' in tag
        assert 'generation_id' in tag
        assert 'label' in tag
        assert 'set' in tag
        assert 'timestamp' in tag
        assert tag['type'] == 'tag'

    def test_get_tags_since_filters_by_timestamp(self, db_session, platform, votes_setup):
        """Test that get_tags_since filters by timestamp."""
        tags = platform.get_tags_since(db_session, datetime.max, 0)
        
        assert len(tags) == 0

    def test_get_tags_since_filters_by_id(self, db_session, platform, votes_setup):
        """Test that get_tags_since filters by tag ID."""
        tags = platform.get_tags_since(db_session, datetime.min, votes_setup['tag2'].id)
        
        assert len(tags) == 0

    def test_get_tags_since_multiple_tags(self, db_session, platform, votes_setup):
        """Test getting multiple tags since a point."""
        tags = platform.get_tags_since(db_session, datetime.min, votes_setup['tag1'].id)
        
        assert len(tags) == 1
        assert tags[0]['id'] == votes_setup['tag2'].id
        assert tags[0]['label'] == 'bad'
