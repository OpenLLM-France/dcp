"""Tests for bot management."""
import pytest
from app.models import Bot


class TestBotCreation:
    """Tests for bot creation."""

    def test_create_bot_session_creates_bot(self, db_session, platform):
        """Test that create_bot_session creates a bot."""
        session_id = platform.create_bot_session(
            db_session,
            "test-model-v1",
            "Here is the response: {{prompt}}",
            {"temperature": 0.7}
        )
        
        # Get user_id from session
        user_id = platform.get_user_id(db_session, session_id)
        bot_info = platform.get_bot_info(db_session, user_id)
        
        assert bot_info is not None
        assert bot_info['model_name'] == "test-model-v1"
        assert bot_info['prompt_template'] == "Here is the response: {{prompt}}"
        assert bot_info['config'] == {"temperature": 0.7}

    def test_create_bot_session_with_config(self, db_session, platform):
        """Test creating bot session with configuration."""
        config = {"temperature": 0.8, "top_p": 0.9, "max_tokens": 200}
        session_id = platform.create_bot_session(
            db_session, 
            "config-model",
            "Response: {{prompt}}",
            config
        )
        
        user_id = platform.get_user_id(db_session, session_id)
        bot_info = platform.get_bot_info(db_session, user_id)
        
        assert bot_info['config'] == config

    def test_create_bot_session_with_template(self, db_session, platform):
        """Test creating bot session with prompt template."""
        template = "You are a helpful assistant. User: {{prompt}} Assistant:"
        session_id = platform.create_bot_session(
            db_session, 
            "template-model",
            template,
            {}
        )
        
        user_id = platform.get_user_id(db_session, session_id)
        bot_info = platform.get_bot_info(db_session, user_id)
        
        assert bot_info['prompt_template'] == template

    def test_create_bot_session_reuses_existing(self, db_session, platform):
        """Test that creating same bot session reuses existing bot."""
        session_id_1 = platform.create_bot_session(
            db_session,
            "reuse-model",
            "Template",
            {"config": 1}
        )
        
        # Get the user_id for this bot
        user_id_1 = platform.get_user_id(db_session, session_id_1)
        
        # Create another user and try to create same bot
        session_id_2, user_id_2 = platform.add_user(db_session)
        session_id_2 = platform.create_bot_session(
            db_session,
            "reuse-model",
            "Template",
            {"config": 1}
        )
        
        # Should reuse existing bot (same user as first bot)
        user_id_from_session_2 = platform.get_user_id(db_session, session_id_2)
        
        # The session should belong to the same user as the first bot
        assert user_id_from_session_2 == user_id_1
        bot_info_2 = platform.get_bot_info(db_session, user_id_from_session_2)
        assert bot_info_2 is not None
        assert bot_info_2['model_name'] == "reuse-model"

    def test_create_bot_session_generates_new_session(self, db_session, platform):
        """Test that create_bot_session returns a session ID."""
        session_id = platform.create_bot_session(
            db_session,
            "session-model",
            "Template",
            {}
        )
        
        # Session ID should be a valid UUID
        import uuid
        assert session_id is not None
        # Verify it's a valid UUID by trying to parse it
        uuid.UUID(str(session_id))


class TestBotRetrieval:
    """Tests for retrieving bots."""

    def test_get_bot_info_exists(self, db_session, platform, seeded_bot):
        """Test retrieving bot info when it exists."""
        bot_info = seeded_bot['bot_info']
        assert bot_info is not None
        assert bot_info['model_name'] == "test-model-v1"

    def test_get_bot_info_not_found(self, db_session, platform):
        """Test retrieving bot info when no bot exists."""
        # Create a fresh user without creating a bot
        session_id, user_id = platform.add_user(db_session)
        
        bot_info = platform.get_bot_info(db_session, user_id)
        assert bot_info is None


class TestBotSession:
    """Tests for bot session functionality."""

    def test_bot_session_id_valid(self, db_session, platform):
        """Test that bot session returns valid session ID."""
        session_id = platform.create_bot_session(
            db_session,
            "valid-session-model",
            "Template",
            {}
        )
        
        # Verify session exists
        user_id = platform.get_user_id(db_session, session_id)
        assert user_id is not None

    def test_multiple_bots_different_models(self, db_session, platform):
        """Test creating multiple bots with different models."""
        session_id_1 = platform.create_bot_session(
            db_session,
            "model-a",
            "Template A",
            {}
        )
        
        session_id_2 = platform.create_bot_session(
            db_session,
            "model-b", 
            "Template B",
            {}
        )
        
        user_id_1 = platform.get_user_id(db_session, session_id_1)
        user_id_2 = platform.get_user_id(db_session, session_id_2)
        
        bot_info_1 = platform.get_bot_info(db_session, user_id_1)
        bot_info_2 = platform.get_bot_info(db_session, user_id_2)
        
        assert bot_info_1['model_name'] == "model-a"
        assert bot_info_2['model_name'] == "model-b"

    def test_get_user_bot_with_bots(self, db_session, platform):
        """Test get_user_bot returns users with their bot models."""
        session_id_1 = platform.create_bot_session(
            db_session,
            "bot-model-1",
            "Template 1",
            {}
        )
        
        session_id_2 = platform.create_bot_session(
            db_session,
            "bot-model-2",
            "Template 2",
            {}
        )
        
        result = platform.get_user_bot(db_session)
        
        assert len(result) >= 2
        models = [item['model_name'] for item in result]
        assert "bot-model-1" in models
        assert "bot-model-2" in models

    def test_get_user_bot_with_users_without_bots(self, db_session, platform):
        """Test get_user_bot includes users without bots (model_name is None)."""
        session_id = platform.create_bot_session(
            db_session,
            "bot-with-user",
            "Template",
            {}
        )
        user_id_with_bot = platform.get_user_id(db_session, session_id)
        
        session_id_2, user_id_without_bot = platform.add_user(db_session)
        
        result = platform.get_user_bot(db_session)
        
        assert len(result) >= 2
        user_models = {item['user_id']: item['model_name'] for item in result}
        
        assert user_models[user_id_with_bot] == "bot-with-user"
        assert user_models[user_id_without_bot] is None
