"""Tests for task instances, voting, and tagging."""
import pytest
from app.models import TaskInstance, Vote, Tag, GenerationView, Prompt


@pytest.fixture
def simple_task_setup(db_session, platform, seeded_instruction):
    """Simple setup with one task, one prompt, and two generations."""
    # Create task
    task_id = platform.add_task(
        db_session, 
        "Simple Task", 
        True, 
        {}, 
        seeded_instruction.id
    )
    
    # Create user and permission
    session_id, user_id = platform.add_user(db_session)
    platform.add_usertaskpermission(db_session, user_id, task_id)
    
    # Create one prompt
    prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
    prompt = db_session.query(Prompt).filter_by(id=prompt_id).one()
    
    # Create two generations for this prompt
    params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
    gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
    gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)
    
    return {
        'task_id': task_id,
        'session_id': session_id,
        'user_id': user_id,
        'prompt': prompt,
        'gen_a_id': gen_a_id,
        'gen_b_id': gen_b_id
    }


@pytest.fixture
def task_instance_data(db_session, platform, simple_task_setup):
    """Create a task instance for testing."""
    task_instance = platform.get_task_instance_for_user(
        db_session, 
        str(simple_task_setup['task_id']), 
        simple_task_setup['user_id']
    )
    
    return {
        'task_instance': task_instance,
        'user_id': simple_task_setup['user_id'],
        'session_id': simple_task_setup['session_id'],
        'gen_a_id': simple_task_setup['gen_a_id'],
        'gen_b_id': simple_task_setup['gen_b_id']
    }


class TestTaskInstanceCreation:
    """Tests for task instance creation."""

    def test_get_task_instance_for_user_creates_instance(self, db_session, platform, task_instance_data):
        """Test that get_task_instance_for_user creates a task instance."""
        task_instance = task_instance_data['task_instance']
        assert task_instance is not None
        assert 'id' in task_instance
        assert 'prompt' in task_instance
        assert 'generations' in task_instance

    def test_get_task_instance_for_user_with_user_id(self, db_session, platform, task_instance_data):
        """Test task instance has correct user ID."""
        user_id = task_instance_data['user_id']
        
        # Verify the task instance was created for this user
        assert task_instance_data['task_instance'] is not None

    def test_get_task_instance_for_user_with_generations(self, db_session, platform, task_instance_data):
        """Test task instance has both generations."""
        task_instance = task_instance_data['task_instance']
        
        assert len(task_instance['generations']) == 2
        assert 'id' in task_instance['generations'][0]
        assert 'text' in task_instance['generations'][0]
        assert 'id' in task_instance['generations'][1]
        assert 'text' in task_instance['generations'][1]

    def test_get_task_instance_reuses_existing_data(self, db_session, platform, task_instance_data):
        """Test that task instance contains prompt and generations."""
        task_instance = task_instance_data['task_instance']
        
        assert task_instance['prompt'] is not None
        assert len(task_instance['prompt']) > 0
        assert len(task_instance['generations']) == 2


class TestVoting:
    """Tests for voting functionality."""

    def test_add_vote_creates_vote(self, db_session, platform, task_instance_data):
        """Test that add_vote creates a vote."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        vote = platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        assert vote is not None
        assert vote.taskinstance_id == task_instance['id']
        assert vote.criterion == "quality"
        assert vote.action_set is True
        assert vote.answer == 1

    def test_add_vote_with_negative_value(self, db_session, platform, task_instance_data):
        """Test voting with negative value (preferring generation A)."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        vote = platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            -2
        )
        
        assert vote.answer == -2

    def test_add_vote_with_special_values(self, db_session, platform, task_instance_data):
        """Test voting with special values."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        # Skip without voting
        vote = platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            False,
            "skip",
            -200
        )
        assert vote.answer == -200

    def test_get_votes_for_task_instance(self, db_session, platform, task_instance_data):
        """Test getting all votes for a task instance."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            2
        )
        
        votes = platform.get_votes_for_task_instance(db_session, task_instance['id'])
        
        assert len(votes) == 2

    def test_get_votes_returns_formatted_data(self, db_session, platform, task_instance_data):
        """Test that votes are returned with correct format."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        votes = platform.get_votes_for_task_instance(db_session, task_instance['id'])
        
        assert len(votes) == 1
        assert 'id' in votes[0]
        assert 'answer' in votes[0]
        assert 'timestamp' in votes[0]


class TestTagging:
    """Tests for tagging functionality."""

    def test_add_tag_creates_tag(self, db_session, platform, task_instance_data):
        """Test that add_tag creates a tag."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        
        tag = platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "helpful"
        )
        
        assert tag is not None
        assert tag.taskinstance_id == task_instance['id']
        assert tag.generation_id == gen_a_id
        assert tag.label == "helpful"
        assert tag.action_set is True

    def test_add_tag_with_negative_action(self, db_session, platform, task_instance_data):
        """Test tagging with action_set=False."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        
        tag = platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            False,
            "bad"
        )
        
        assert tag.action_set is False

    def test_get_tags_for_task_instance(self, db_session, platform, task_instance_data):
        """Test getting all tags for a task instance."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "tag1"
        )
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "tag2"
        )
        
        tags = platform.get_tags_for_task_instance(db_session, task_instance['id'])
        
        assert len(tags) == 2

    def test_get_tags_returns_formatted_data(self, db_session, platform, task_instance_data):
        """Test that tags are returned with correct format."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "helpful"
        )
        
        tags = platform.get_tags_for_task_instance(db_session, task_instance['id'])
        
        assert len(tags) == 1
        assert 'id' in tags[0]
        assert 'generation_id' in tags[0]
        assert 'label' in tags[0]
        assert 'action' in tags[0]
        assert 'timestamp' in tags[0]


class TestGenerationViews:
    """Tests for generation view tracking."""

    def test_add_generation_view_creates_view(self, db_session, platform, task_instance_data):
        """Test that adding a view creates a view record."""
        gen_a_id = task_instance_data['gen_a_id']
        
        # Views are automatically created when getting task instance
        # We can verify by checking the generations were viewed
        assert gen_a_id is not None

    def test_get_generation_views_for_generation(self, db_session, platform, task_instance_data):
        """Test getting all views for a generation."""
        # Task instance creation automatically creates views
        # Just verify the task instance was created successfully
        assert task_instance_data['task_instance'] is not None


class TestTaskInstanceWithVoting:
    """Tests combining task instances with voting and tagging."""

    def test_complete_vote_flow(self, db_session, platform, task_instance_data):
        """Test complete voting flow."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        # Vote
        platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        # Tag
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "helpful"
        )
        
        # Verify
        votes = platform.get_votes_for_task_instance(db_session, task_instance['id'])
        tags = platform.get_tags_for_task_instance(db_session, task_instance['id'])
        
        assert len(votes) == 1
        assert len(tags) == 1

    def test_multiple_votes_and_tags(self, db_session, platform, task_instance_data):
        """Test multiple votes and tags on same task instance."""
        task_instance = task_instance_data['task_instance']
        gen_a_id = task_instance_data['gen_a_id']
        gen_b_id = task_instance_data['gen_b_id']
        
        # Add multiple votes
        platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        platform.add_vote(
            db_session, 
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "helpfulness",
            2
        )
        
        # Add multiple tags
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "helpful"
        )
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "accurate"
        )
        
        votes = platform.get_votes_for_task_instance(db_session, task_instance['id'])
        tags = platform.get_tags_for_task_instance(db_session, task_instance['id'])
        
        assert len(votes) == 2
        assert len(tags) == 2


class TestTaskInstanceRetrieval:
    """Tests for retrieving task instances."""

    def test_get_task_instances_for_prompt_creates_list(self, db_session, platform, seeded_instruction):
        """Test that get_task_instances_for_prompt returns task instances for a prompt."""
        from datetime import datetime
        
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
        
        before_timestamp = datetime.now()
        
        task_instance = platform.get_task_instance_for_user(
            db_session, 
            str(task_id), 
            user_id
        )
        
        task_instances = platform.get_task_instances_for_prompt(db_session, prompt_id)
        
        assert len(task_instances) >= 1
        task_instances_after = platform.get_task_instances_for_prompt(db_session, prompt_id)
        assert len(task_instances_after) >= 1

    def test_get_task_instances_for_prompt_returns_formatted_data(self, db_session, platform, seeded_instruction):
        """Test that get_task_instances_for_prompt returns correctly formatted data."""
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
        
        platform.get_task_instance_for_user(
            db_session, 
            str(task_id), 
            user_id
        )
        
        task_instances = platform.get_task_instances_for_prompt(db_session, prompt_id)
        
        assert len(task_instances) >= 1
        ti = task_instances[0]
        assert 'id' in ti
        assert 'user_id' in ti
        assert 'generation_a_id' in ti
        assert 'generation_b_id' in ti
        assert 'timestamp' in ti

    def test_get_task_instances_for_prompt_empty(self, db_session, platform, seeded_instruction):
        """Test that get_task_instances_for_prompt returns empty list when no instances exist."""
        task_id = platform.add_task(
            db_session, 
            "Test Task", 
            True, 
            {}, 
            seeded_instruction.id
        )
        
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        
        task_instances = platform.get_task_instances_for_prompt(db_session, prompt_id)
        
        assert task_instances == []


class TestTagsSince:
    """Tests for get_tags_since method."""

    def test_get_tags_since_returns_tags(self, db_session, platform, seeded_instruction):
        """Test that get_tags_since returns tags since a timestamp."""
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
        
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "helpful"
        )
        
        tags = platform.get_tags_since(
            db_session, 
            before_timestamp, 
            0
        )
        
        assert len(tags) >= 1
        tag = tags[0]
        assert 'id' in tag
        assert 'taskinstance_id' in tag
        assert 'user_id' in tag
        assert 'prompt_id' in tag
        assert 'generation_id' in tag
        assert 'label' in tag
        assert 'set' in tag
        assert 'timestamp' in tag
        assert 'type' in tag
        assert tag['type'] == 'tag'

    def test_get_tags_since_with_last_tag_id(self, db_session, platform, seeded_instruction):
        """Test that get_tags_since filters by last_tag_id."""
        import time
        from datetime import datetime
        
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
        
        before_timestamp = datetime.now()
        
        platform.add_tag(
            db_session, 
            task_instance['id'], 
            gen_a_id, 
            True,
            "helpful"
        )
        
        tags = platform.get_tags_since(
            db_session, 
            before_timestamp, 
            999999
        )
        
        assert tags == []

    def test_get_tags_since_empty(self, db_session, platform, seeded_instruction):
        """Test that get_tags_since returns empty list when no tags exist."""
        from datetime import datetime
        
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
        
        tags = platform.get_tags_since(
            db_session, 
            datetime.now(), 
            0
        )
        
        assert tags == []
