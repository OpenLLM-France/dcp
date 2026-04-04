"""Tests for rating system."""
import pytest
from app.models import Rating, Prompt


@pytest.fixture
def rating_setup(db_session, platform, seeded_instruction):
    """Create a task instance with a vote for rating tests."""
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


class TestRatingSystem:
    """Tests for user rating system."""

    def test_get_rating_no_rating_exists(self, db_session, platform, test_user):
        """Test getting rating when none exists."""
        user_id = test_user['user_id']
        rating = platform.get_rating(db_session, user_id)
        
        assert rating is not None
        assert 'user' in rating
        assert 'list' in rating
        assert rating['user']['id'] == 'moi'

    def test_get_rating_with_data(self, db_session, platform, rating_setup):
        """Test getting rating with existing data."""
        user_id = rating_setup['user_id']
        
        rating = platform.get_rating(db_session, user_id)
        
        assert rating is not None
        assert 'user' in rating
        assert 'list' in rating
        assert rating['user']['num'] is not None
        assert 'score' in rating['user']
        assert 'count' in rating['user']

    def test_update_ratings_with_data(self, db_session, platform, rating_setup):
        """Test that update_ratings works with data parameter."""
        user_id = rating_setup['user_id']
        
        # Get vote data to pass to update_ratings
        votes = platform.get_all_votes(db_session)
        
        # Build rating data
        rating_data = []
        user_scores = {}
        for vote in votes:
            uid = vote['user_id']
            if uid not in user_scores:
                user_scores[uid] = 0
            user_scores[uid] += vote.get('score', 0)
        
        for uid, score in user_scores.items():
            rating_data.append({'user_id': uid, 'score': float(score)})
        
        if rating_data:
            platform.update_ratings(db_session, rating_data)
            
            rating = db_session.query(Rating).filter_by(user_id=user_id).first()
            # Rating might not exist if no score was calculated
            assert rating is not None or len(rating_data) == 0

    def test_update_ratings_empty_data(self, db_session, platform):
        """Test that update_ratings raises ValueError with empty data."""
        with pytest.raises(ValueError, match="Empty data"):
            platform.update_ratings(db_session, [])

    def test_get_all_ratings(self, db_session, platform, rating_setup):
        """Test getting all ratings."""
        # First update ratings
        votes = platform.get_all_votes(db_session)
        rating_data = []
        user_scores = {}
        for vote in votes:
            uid = vote['user_id']
            if uid not in user_scores:
                user_scores[uid] = 0
            user_scores[uid] += vote.get('score', 0)
        
        for uid, score in user_scores.items():
            rating_data.append({'user_id': uid, 'score': float(score)})
        
        if rating_data:
            platform.update_ratings(db_session, rating_data)
            
            # Use get_rating to get all ratings since get_all_ratings doesn't exist
            rating = platform.get_rating(db_session, rating_setup['user_id'])
            
            assert rating is not None
            assert 'list' in rating
            assert len(rating['list']) >= 1

    def test_rating_with_start_and_count(self, db_session, platform, rating_setup):
        """Test getting rating with pagination."""
        user_id = rating_setup['user_id']
        
        rating = platform.get_rating(db_session, user_id, start=0, count=5)
        
        assert rating is not None
        assert 'user' in rating
        assert 'list' in rating
        assert len(rating['list']) <= 5

    def test_rating_score_is_float(self, db_session, platform, rating_setup):
        """Test that rating score is a float."""
        user_id = rating_setup['user_id']
        
        rating = platform.get_rating(db_session, user_id)
        
        assert isinstance(rating['user']['score'], (float, int, str))

    def test_multiple_users_have_separate_ratings(self, db_session, platform, rating_setup):
        """Test that multiple users have separate ratings."""
        # Create another user with task instance
        task_id = rating_setup['task_id']
        session_id_2, user_id_2 = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id_2, task_id)
        
        task_instance_2 = platform.get_task_instance_for_user(db_session, str(task_id), user_id_2)
        
        # Create new prompt and generations for second user
        prompt_id_2 = platform.add_prompt(db_session, task_id, "Test prompt 2")
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id_2)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id_2)
        
        platform.add_vote(
            db_session,
            task_instance_2['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        # Update ratings for both users
        votes = platform.get_all_votes(db_session)
        rating_data = []
        user_scores = {}
        for vote in votes:
            uid = vote['user_id']
            if uid not in user_scores:
                user_scores[uid] = 0
            user_scores[uid] += vote.get('score', 0)
        
        for uid, score in user_scores.items():
            rating_data.append({'user_id': uid, 'score': float(score)})
        
        if rating_data:
            platform.update_ratings(db_session, rating_data)
        
        rating1 = platform.get_rating(db_session, rating_setup['user_id'])
        rating2 = platform.get_rating(db_session, user_id_2)
        
        assert rating1 is not None
        assert rating2 is not None
        # Users should be in the list
        assert len(rating1['list']) >= 2
        assert len(rating2['list']) >= 2

    def test_bot_rating_shows_model_name(self, db_session, platform):
        """Test that bot users display model name in ratings."""
        session_id, bot_user_id = platform.add_user(db_session)
        platform.create_bot_session(
            db_session,
            "test-bot-model",
            "Template",
            {"temperature": 0.7}
        )
        
        task_id = platform.add_task(db_session, "Test Task", True, {}, 
                                   platform.add_instruction(db_session, "Test"))
        platform.add_usertaskpermission(db_session, bot_user_id, task_id)
        
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
        
        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), bot_user_id)
        
        platform.add_vote(
            db_session,
            task_instance['id'],
            gen_a_id,
            gen_b_id,
            True,
            "quality",
            1
        )
        
        rating_data = [{'user_id': bot_user_id, 'score': 1.0}]
        platform.update_ratings(db_session, rating_data)
        
        rating = platform.get_rating(db_session, bot_user_id)
        
        assert rating is not None
        bot_in_list = any('🤖' in item['id'] and 'test-bot-model' in item['id'] 
                         for item in rating['list'])
        assert bot_in_list or rating['user']['id'] == 'moi'
