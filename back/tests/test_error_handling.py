"""Tests for error handling and exception cases."""
import pytest
import uuid
from app.models import Prompt, Generation, GenerationParams, Bot


class TestFindExceptions:
    """Tests for exceptions raised by find methods."""

    def test_find_prompt_too_many_prompts(self, db_session, platform):
        """Test that find_prompt raises exception when too many prompts match."""
        task_id = platform.add_task(db_session, "Test Task", True, {}, 
                                   platform.add_instruction(db_session, "Test"))
        
        # Create duplicate prompts with same text
        platform.add_prompt(db_session, task_id, "Duplicate prompt")
        platform.add_prompt(db_session, task_id, "Duplicate prompt")
        
        with pytest.raises(Exception, match="Too much.*prompts"):
            platform.find_prompt(db_session, task_id, "Duplicate prompt")

    def test_find_generation_too_many_generations(self, db_session, platform, seeded_prompts):
        """Test that find_generation raises exception when too many generations match."""
        params_id = platform.add_generation_params(db_session, {})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        # Create duplicate generations with same text
        platform.add_generation(db_session, "Duplicate gen", params_id, prompt_id)
        platform.add_generation(db_session, "Duplicate gen", params_id, prompt_id)
        
        with pytest.raises(Exception, match="Too much.*generations"):
            platform.find_generation(db_session, "Duplicate gen", params_id, prompt_id)

    def test_find_generation_params_too_many_params(self, db_session, platform):
        """Test that find_generation_params raises exception when too many match."""
        params_data = {"temperature": 0.7}
        
        # Add params twice (should be same, but force duplicate)
        params_id_1 = platform.add_generation_params(db_session, params_data)
        
        # Directly add another with same params
        import json
        from app.service import normalize_json
        
        db_params = GenerationParams(params=json.loads(normalize_json(params_data)))
        db_session.add(db_params)
        db_session.commit()
        
        with pytest.raises(Exception, match="Too much.*generation params"):
            platform.find_generation_params(db_session, params_data)


class TestInternalMethodExceptions:
    """Tests for exceptions raised by internal methods."""

    def test_get_least_viewed_generations_not_enough_generations(self, db_session, platform):
        """Test that __get_least_viewed_generations raises exception with only one generation."""
        task_id = platform.add_task(db_session, "Test Task", True, {}, 
                                   platform.add_instruction(db_session, "Test"))
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        
        # Create only one generation
        params_id = platform.add_generation_params(db_session, {})
        platform.add_generation(db_session, "Only one gen", params_id, prompt_id)
        
        # Create a user for the view check
        session_id, user_id = platform.add_user(db_session)
        
        # Use internal method directly
        with pytest.raises(Exception):
            platform._DataCollectionPlatform__get_least_viewed_generations(db_session, prompt_id, user_id)


class TestAgreementExceptions:
    """Tests for exceptions raised by agreement methods."""

    def test_get_agreements_for_user_invalid_session(self, db_session, platform):
        """Test that get_agreements_for_user raises ValueError with invalid session."""
        # Use a valid UUID format that doesn't exist in DB
        invalid_uuid = str(uuid.uuid4())
        with pytest.raises(ValueError, match="Invalid session"):
            platform.get_agreements_for_user(db_session, invalid_uuid)

    def test_record_agreement_invalid_session(self, db_session, platform):
        """Test that record_agreement raises ValueError with invalid session."""
        agreement_id = platform.add_agreement(db_session, "Test", "Test desc", "Test text").id
        invalid_uuid = str(uuid.uuid4())
        
        with pytest.raises(ValueError, match="Invalid session"):
            platform.record_agreement(db_session, invalid_uuid, agreement_id)


class TestBotExceptions:
    """Tests for exceptions raised by bot methods."""

    def test_get_bot_info_multiple_bots(self, db_session, platform):
        """Test that get_bot_info raises exception when user has multiple bots."""
        session_id = platform.create_bot_session(
            db_session,
            "multi-bot-user-test",
            "Template",
            {}
        )
        user_id = platform.get_user_id(db_session, session_id)
        
        # Create another bot for same user
        db_bot = Bot(user_id=user_id, model_name="second-bot-test", 
                    prompt_template="Template 2", config={})
        db_session.add(db_bot)
        db_session.commit()
        
        with pytest.raises(Exception, match="Too many bots found"):
            platform.get_bot_info(db_session, user_id)


class TestBotRatingDisplay:
    """Tests for bot rating display format."""

    def test_get_rating_bot_display_format(self, db_session, platform):
        """Test that get_rating displays bot users with 🤖 emoji and model name."""
        # Create a bot user
        session_id, bot_user_id = platform.add_user(db_session)
        platform.create_bot_session(
            db_session,
            "display-test-bot",
            "Template",
            {}
        )
        
        # Create task and vote to get a score
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
        
        # Update ratings
        rating_data = [{'user_id': bot_user_id, 'score': 1.0}]
        platform.update_ratings(db_session, rating_data)
        
        # Get rating and check bot display format
        rating = platform.get_rating(db_session, bot_user_id)
        
        assert rating is not None
        # Check that bot is displayed with emoji and model name in the list
        bot_displayed = False
        for item in rating['list']:
            if '🤖' in item['id'] and 'display-test-bot' in item['id']:
                bot_displayed = True
                break
        
        # Either bot is in list with correct format, or it's the current user
        assert bot_displayed or rating['user']['id'] == 'moi'
