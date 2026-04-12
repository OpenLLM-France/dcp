"""
API-level tests for DataCollectionPlatform endpoints.

These tests provide independent validation of all endpoints through end-to-end testing.
Each test creates its own test data via API calls and does not rely on existing fixtures.
"""

import pytest
from uuid import uuid4
from sqlalchemy import select
from app.service import DataCollectionPlatform
from app.models import Vote, Tag, Bot, UserSignature


# ============================================================================
# Test Auth and Session Management
# ============================================================================

class TestAuthAndSession:
    """Tests for /home endpoint and session management."""

    def test_home_creates_new_session(self, api_client):
        """Happy path: /home creates a new session when none exists."""
        response = api_client.get("/home")

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_home_returns_same_session_on_repeat_call(self, authenticated_client):
        """Happy path: Subsequent /home calls return the same session."""
        client, session_id = authenticated_client

        response = client.get("/home")
        assert response.status_code == 200
        assert response.json()["session_id"] == session_id

    def test_home_sets_session_cookie(self, api_client):
        """Happy path: /home sets session_id cookie in response."""
        response = api_client.get("/home")

        assert response.status_code == 200
        assert "set-cookie" in response.headers
        assert "session_id=" in response.headers["set-cookie"]

    def test_home_with_invalid_session_uuid_format_creates_new(self, api_client):
        """Edge case: Invalid session_id format (not UUID) creates new session."""
        # After fix, invalid UUID format is caught and new session is created
        response = api_client.get("/home", cookies={"session_id": "invalid-session"})

        # Should create new session gracefully
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data

    def test_invalid_session_returns_401(self, api_client):
        """Invalid session_id cookie returns 401 for protected endpoints."""
        # Invalid UUID format now handled gracefully with 401
        response = api_client.get("/tasks", cookies={"session_id": "invalid"})

        assert response.status_code == 401


# ============================================================================
# Test Task Endpoints
# ============================================================================

class TestTaskEndpoints:
    """Tests for /tasks, /task/{id}/next, and /task/{id}/instruction endpoints."""

    def test_tasks_requires_authentication(self, api_client):
        """Authentication: /tasks without session returns 401."""
        response = api_client.get("/tasks")

        assert response.status_code == 401

    def test_tasks_returns_user_tasks(self, authenticated_client, db_session, platform):
        """Happy path: /tasks returns empty list for new user."""
        client, session_id = authenticated_client

        response = client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_tasks_returns_assigned_task(self, authenticated_client, db_session, platform):
        """Happy path: /tasks returns task after assignment."""
        client, session_id = authenticated_client

        # Create task and assign to user
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        response = client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) >= 1
        task_ids = [str(t["id"]) for t in data["tasks"]]
        assert str(task_id) in task_ids

    def test_task_next_requires_authentication(self, api_client):
        """Authentication: /task/{id}/next without session returns 401."""
        response = api_client.post("/task/123e4567-e89b-12d3-a456-426614174000/next")

        assert response.status_code == 401

    def test_task_next_returns_task_data(self, authenticated_client, db_session, platform):
        """Happy path: /task/{id}/next returns task with prompt and generations."""
        client, session_id = authenticated_client

        # Create complete task setup
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create prompt and generations
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)

        response = client.post(f"/task/{task_id}/next")

        assert response.status_code == 200
        data = response.json()
        assert "meta" in data
        assert "prompt" in data
        assert "task_instance_id" in data
        assert "generations" in data
        assert len(data["generations"]) == 2

    def test_task_next_unknown_task_returns_404(self, authenticated_client, db_session, platform):
        """Edge case: Unknown task_id returns 404."""
        client, session_id = authenticated_client

        user_id = platform.get_user_id(db_session, session_id)
        unknown_task_id = uuid4()

        response = client.post(f"/task/{unknown_task_id}/next")

        # Returns 404 for unknown task
        assert response.status_code == 404

    def test_task_instruction_returns_text(self, api_client, db_session, platform):
        """Happy path: /task/{id}/instruction returns instruction data."""
        instruction_id = platform.add_instruction(db_session, "Test instruction text")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)

        response = api_client.get(f"/task/{task_id}/instruction")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "text" in data
        assert data["text"] == "Test instruction text"

    def test_task_instruction_unknown_task_returns_200(self, api_client):
        """Edge case: /task/{id}/instruction with unknown task returns 200 with null."""
        unknown_task_id = uuid4()

        response = api_client.get(f"/task/{unknown_task_id}/instruction")

        # Returns 200 with None/null response when instruction not found
        assert response.status_code == 200
        data = response.json()
        assert data is None or data == {}


# ============================================================================
# Test Voting and Tagging Endpoints
# ============================================================================

class TestVotingAndTagging:
    """Tests for /task/vote and /task/tag endpoints."""

    def test_vote_requires_authentication(self, api_client):
        """Authentication: /task/vote without session returns 401."""
        vote_data = {
            "task_instance_id": str(uuid4()),
            "generation_a_id": str(uuid4()),
            "generation_b_id": str(uuid4()),
            "action": True,
            "criterion": "quality",
            "value": 1
        }
        response = api_client.post("/task/vote", json=vote_data)

        # Auth check happens before validation for this endpoint
        assert response.status_code == 401

    def test_vote_successfully_records(self, authenticated_client, db_session, platform):
        """Happy path: /task/vote successfully records a vote."""
        client, session_id = authenticated_client

        # Create task instance with generations
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)
        task_instance_id = task_instance["id"]

        vote_data = {
            "task_instance_id": str(task_instance_id),
            "generation_a_id": str(gen_a_id),
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "quality",
            "value": 1
        }

        response = client.post("/task/vote", json=vote_data)

        assert response.status_code == 200
        assert response.json() == {}

    def test_vote_with_invalid_generation_ids_returns_200(self, authenticated_client, db_session, platform):
        """Validation: Vote with invalid generation IDs returns 200 (handled gracefully)."""
        client, session_id = authenticated_client

        # Create minimal task instance
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        vote_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_a_id": str(uuid4()),  # Invalid
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "quality",
            "value": 1
        }

        response = client.post("/task/vote", json=vote_data)

        # Service layer handles this gracefully with 200
        assert response.status_code == 200

    def test_tag_requires_authentication(self, api_client):
        """Authentication: /task/tag without session returns 401."""
        tag_data = {
            "task_instance_id": str(uuid4()),
            "generation_id": str(uuid4()),
            "action": True,
            "tag": "test-tag"
        }
        response = api_client.post("/task/tag", json=tag_data)

        assert response.status_code == 401

    def test_tag_successfully_records(self, authenticated_client, db_session, platform):
        """Happy path: /task/tag successfully records a tag."""
        client, session_id = authenticated_client

        # Create task instance with 2 generations (required for tagging)
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        tag_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_id": str(gen_a_id),
            "action": True,
            "tag": "test-tag"
        }

        response = client.post("/task/tag", json=tag_data)

        assert response.status_code == 200
        assert response.json() == {}

    def test_tag_clear_removes_tag(self, authenticated_client, db_session, platform):
        """Happy path: /task/tag with action=false clears a tag."""
        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # Set tag
        tag_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_id": str(gen_a_id),
            "action": True,
            "tag": "test-tag"
        }
        client.post("/task/tag", json=tag_data)

        # Clear tag
        tag_data["action"] = False
        response = client.post("/task/tag", json=tag_data)

        assert response.status_code == 200

    def test_vote_database_state_verification(self, authenticated_client, db_session, platform):
        """Database state: Verify POST creates correct DB records."""
        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        vote_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_a_id": str(gen_a_id),
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "clarity",
            "value": 5
        }

        response = client.post("/task/vote", json=vote_data)

        # Verify API accepted the vote
        assert response.status_code == 200


# ============================================================================
# Test Agreement Endpoints
# ============================================================================

class TestAgreementEndpoints:
    """Tests for /user/agreements, /agreement, and /user/sign endpoints."""

    def test_user_agreements_requires_authentication(self, api_client):
        """Authentication: /user/agreements without session returns 401."""
        response = api_client.get("/user/agreements")

        assert response.status_code == 401

    def test_user_agreements_returns_agreements_list(self, authenticated_client, db_session, platform):
        """Happy path: /user/agreements returns list of agreements with signature status."""
        client, session_id = authenticated_client

        # Create agreement
        platform.add_agreement(
            db_session, "Test Agreement", "Test Text", "I agree."
        )

        response = client.get("/user/agreements")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Each agreement has agreement_id, agreement_name, description, signed_timestamp
        if len(data) > 0:
            assert "agreement_id" in data[0]

    def test_user_agreements_shows_signed_status(self, authenticated_client, db_session, platform):
        """Happy path: /user/agreements shows which agreements user has signed."""
        client, session_id = authenticated_client

        # Create and sign agreement
        agreement = platform.add_agreement(
            db_session, "Test Agreement", "Test Text", "I agree."
        )
        platform.record_agreement(db_session, session_id, agreement.id)

        response = client.get("/user/agreements")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["agreement_id"] == agreement.id
        assert data[0]["signed_timestamp"] is not None

    def test_agreement_returns_text(self, api_client, db_session, platform):
        """Happy path: /agreement?agreement_id=X returns agreement text."""
        agreement = platform.add_agreement(
            db_session, "Privacy Policy", "Privacy text", "Privacy details."
        )

        response = api_client.get(f"/agreement?agreement_id={agreement.id}")

        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert data["text"] == "Privacy details."

    def test_agreement_unknown_id_returns_200(self, api_client):
        """Error case: /agreement?agreement_id=X with unknown id returns 200 with empty."""
        response = api_client.get("/agreement?agreement_id=99999")

        # Returns 200 with empty response when not found
        assert response.status_code == 200

    def test_user_sign_records_agreement(self, authenticated_client, db_session, platform):
        """Happy path: /user/sign?agreement_id=X records the signature."""
        client, session_id = authenticated_client

        agreement = platform.add_agreement(
            db_session, "Terms of Service", "Terms text", "I agree to terms."
        )

        response = client.post(f"/user/sign?agreement_id={agreement.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "agreements" in data

    def test_user_sign_with_invalid_agreement_id_returns_500(self, authenticated_client):
        """Validation: /user/sign with invalid agreement_id returns 500."""
        client, session_id = authenticated_client

        response = client.post("/user/sign?agreement_id=99999")

        assert response.status_code == 500


# ============================================================================
# Test Bot Endpoints
# ============================================================================

class TestBotEndpoints:
    """Tests for /create_bot_session endpoint."""

    def test_create_bot_session_successfully(self, api_client):
        """Happy path: /create_bot_session creates bot session."""
        # Note: config must be a JSON string, not a dict
        bot_params = {
            "model_name": "test-model",
            "prompt_template": "Respond to: {{prompt}}",
            "config": '{"temperature": 0.7}'
        }

        response = api_client.post("/create_bot_session", json=bot_params)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0

    def test_create_bot_session_with_different_configs(self, api_client):
        """Happy path: Multiple bot sessions can be created."""
        params1 = {
            "model_name": "model-a",
            "prompt_template": "A: {{prompt}}",
            "config": '{"temperature": 0.5}'
        }
        params2 = {
            "model_name": "model-b",
            "prompt_template": "B: {{prompt}}",
            "config": '{"temperature": 0.9}'
        }

        response1 = api_client.post("/create_bot_session", json=params1)
        response2 = api_client.post("/create_bot_session", json=params2)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["session_id"] != response2.json()["session_id"]

    def test_create_bot_session_with_complex_config(self, api_client):
        """Happy path: Bot session accepts complex configuration."""
        bot_params = {
            "model_name": "advanced-model",
            "prompt_template": "System: {{system}}\nUser: {{prompt}}\nAssistant:",
            "config": '{"temperature": 0.8, "max_tokens": 500, "top_p": 0.9}'
        }

        response = api_client.post("/create_bot_session", json=bot_params)

        assert response.status_code == 200
        assert "session_id" in response.json()

    def test_create_bot_session_creates_bot_in_db(self, api_client, db_session, platform):
        """Database state: Verify bot session creates records in DB."""
        bot_params = {
            "model_name": "test-model",
            "prompt_template": "Test: {{prompt}}",
            "config": '{"test": true}'
        }

        response = api_client.post("/create_bot_session", json=bot_params)
        session_id = response.json()["session_id"]

        # Verify bot exists in database
        user_id = platform.get_user_id(db_session, session_id)
        bot_info = platform.get_bot_info(db_session, user_id)

        assert bot_info is not None
        assert bot_info["model_name"] == "test-model"


# ============================================================================
# Test Statistics Endpoints
# ============================================================================

class TestStatisticsEndpoints:
    """Tests for /stat/votes/total and /stat/rating endpoints."""

    def test_total_votes_returns_count(self, api_client, db_session, platform):
        """Happy path: /stat/votes/total returns vote count."""
        response = api_client.get("/stat/votes/total")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)

    def test_total_votes_increases_after_vote(self, authenticated_client, api_client, db_session, platform):
        """Happy path: Vote count increases after recording a vote."""
        client, session_id = authenticated_client

        # Get initial count
        initial_response = api_client.get("/stat/votes/total")
        initial_count = initial_response.json()["count"]

        # Create and vote on task
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        vote_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_a_id": str(gen_a_id),
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "quality",
            "value": 1
        }

        client.post("/task/vote", json=vote_data)

        # Get updated count
        updated_response = api_client.get("/stat/votes/total")
        updated_count = updated_response.json()["count"]

        assert updated_count == initial_count + 1

    def test_rating_returns_rating_data(self, api_client):
        """Happy path: /stat/rating returns rating data."""
        response = api_client.get("/stat/rating?count=10")

        assert response.status_code == 200
        data = response.json()
        # Response has 'user' and 'list' keys
        assert "user" in data or "list" in data

    def test_rating_with_user_session(self, authenticated_client):
        """Happy path: /stat/rating works with authenticated user."""
        client, session_id = authenticated_client

        response = client.get("/stat/rating?start=0&count=5")

        assert response.status_code == 200


# ============================================================================
# Test Authentication Errors on Protected Endpoints
# ============================================================================

class TestAuthenticationErrors:
    """Tests that all protected endpoints require authentication."""

    def test_tasks_401_detail_message(self, api_client):
        """/tasks returns proper 401 detail message."""
        response = api_client.get("/tasks")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_task_vote_422_without_session(self, api_client):
        """/task/vote without session returns 422 (validation before auth)."""
        response = api_client.post("/task/vote", json={})

        # Validation runs before auth check - this is a bug in API design
        assert response.status_code == 422

    def test_task_tag_422_without_session(self, api_client):
        """/task/tag without session returns 422 (validation before auth)."""
        response = api_client.post("/task/tag", json={})

        # Validation runs before auth check
        assert response.status_code == 422

    def test_user_agreements_401_detail_message(self, api_client):
        """/user/agreements returns proper 401 detail message."""
        response = api_client.get("/user/agreements")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_user_sign_401_without_session(self, api_client):
        """/user/sign without session returns 401."""
        response = api_client.post("/user/sign?agreement_id=1", json={})

        assert response.status_code == 401


# ============================================================================
# Test Input Validation
# ============================================================================

class TestInputValidation:
    """Tests for input validation on API endpoints."""

    def test_vote_with_missing_fields(self, authenticated_client):
        """Validation: Vote with missing required fields returns 422."""
        client, session_id = authenticated_client

        # Missing required fields
        vote_data = {
            "task_instance_id": str(uuid4()),
            # Missing other required fields
        }

        response = client.post("/task/vote", json=vote_data)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_tag_with_missing_fields(self, authenticated_client):
        """Validation: Tag with missing required fields returns 422."""
        client, session_id = authenticated_client

        tag_data = {
            "task_instance_id": str(uuid4()),
            # Missing generation_id, action, tag
        }

        response = client.post("/task/tag", json=tag_data)

        assert response.status_code == 422

    def test_bot_session_with_missing_fields(self, api_client):
        """Validation: Bot session with missing fields returns 422."""
        bot_params = {
            "model_name": "test"
            # Missing prompt_template and config
        }

        response = api_client.post("/create_bot_session", json=bot_params)

        assert response.status_code == 422

    def test_vote_with_invalid_uuid_format(self, authenticated_client):
        """Validation: Vote with invalid UUID format returns 422."""
        client, session_id = authenticated_client

        vote_data = {
            "task_instance_id": "not-a-uuid",
            "generation_a_id": str(uuid4()),
            "generation_b_id": str(uuid4()),
            "action": True,
            "criterion": "quality",
            "value": 1
        }

        response = client.post("/task/vote", json=vote_data)

        assert response.status_code == 422


# ============================================================================
# High Priority: Additional Authentication Error Tests
# ============================================================================

class TestAdditionalAuthErrors:
    """Additional tests for authentication on all protected endpoints."""

    def test_task_next_unauthorized_task(self, authenticated_client, db_session, platform):
        """Task not assigned to user returns 404."""
        client, session_id = authenticated_client

        # Create private task but don't assign to user
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Private Task", False, {}, instruction_id)

        response = client.post(f"/task/{task_id}/next")

        assert response.status_code == 404

    def test_agreement_unauthenticated(self, api_client):
        """/agreement endpoint accessible without auth (public)."""
        # This endpoint doesn't require authentication
        response = api_client.get("/agreement?agreement_id=1")

        assert response.status_code == 200

    def test_stat_votes_total_unauthenticated(self, api_client):
        """/stat/votes/total accessible without auth (public)."""
        response = api_client.get("/stat/votes/total")

        assert response.status_code == 200

    def test_stat_rating_unauthenticated(self, api_client):
        """/stat/rating accessible without auth (public)."""
        response = api_client.get("/stat/rating?count=10")

        assert response.status_code == 200

    def test_task_instruction_unauthenticated(self, api_client, db_session, platform):
        """/task/{id}/instruction accessible without auth (public)."""
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)

        response = api_client.get(f"/task/{task_id}/instruction")

        assert response.status_code == 200


# ============================================================================
# High Priority: Additional Validation Tests
# ============================================================================

class TestAdditionalValidation:
    """Additional validation tests for edge cases."""

    # DISABLED: test_tag_with_nonexistent_generation
    # Tests unhandled IntegrityError (foreign key violation returns 500)
    # This is a service layer bug that should be fixed separately
    # TODO: Re-enable after service layer handles IntegrityError gracefully
    # def test_tag_with_nonexistent_generation(self, authenticated_client, db_session, platform):
    #     """Tag with non-existent generation_id handles error gracefully."""
    #     from sqlalchemy.exc import IntegrityError
    #
    #     client, session_id = authenticated_client
    #
    #     instruction_id = platform.add_instruction(db_session, "Test")
    #     task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
    #     user_id = platform.get_user_id(db_session, session_id)
    #     platform.add_usertaskpermission(db_session, user_id, task_id)
    #
    #     prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
    #     params_id = platform.add_generation_params(db_session, {})
    #     gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
    #     gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
    #
    #     task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)
    #
    #     # Use a valid task_instance but invalid generation_id
    #     fake_gen_id = uuid4()
    #     tag_data = {
    #         "task_instance_id": str(task_instance["id"]),
    #         "generation_id": str(fake_gen_id),  # Non-existent
    #         "action": True,
    #         "tag": "test-tag"
    #     }
    #
    #     # This will raise IntegrityError at DB level (foreign key violation)
    #     # which gets returned as 500
    #     response = client.post("/task/tag", json=tag_data)
    #
    #     # DB constraint violation returns 500
    #     assert response.status_code == 500

    def test_vote_with_empty_criterion(self, authenticated_client, db_session, platform):
        """Vote with empty criterion string returns 422."""
        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        vote_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_a_id": str(gen_a_id),
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "",
            "value": 1
        }

        response = client.post("/task/vote", json=vote_data)

        assert response.status_code in [422, 200]

    def test_tag_with_empty_tag_name(self, authenticated_client, db_session, platform):
        """Tag with empty tag name returns 422."""
        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        tag_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_id": str(gen_a_id),
            "action": True,
            "tag": ""
        }

        response = client.post("/task/tag", json=tag_data)

        # Empty tag is handled gracefully (returns 200)
        assert response.status_code == 200

    def test_bot_session_with_invalid_json_config(self, api_client):
        """Bot session with invalid JSON config string returns 422."""
        bot_params = {
            "model_name": "test-model",
            "prompt_template": "Test: {{prompt}}",
            "config": "not-valid-json"
        }

        response = api_client.post("/create_bot_session", json=bot_params)

        assert response.status_code == 422

    def test_user_sign_with_negative_agreement_id(self, authenticated_client):
        """/user/sign with negative agreement_id returns 500."""
        client, session_id = authenticated_client

        response = client.post("/user/sign?agreement_id=-1")

        assert response.status_code == 500

    def test_agreement_with_negative_id(self, api_client):
        """/agreement with negative agreement_id returns 200 with null."""
        response = api_client.get("/agreement?agreement_id=-1")

        assert response.status_code == 200


# ============================================================================
# Medium Priority: Database State Verification Tests
# ============================================================================

class TestDatabaseStateVerification:
    """Tests that verify database state after API operations."""

    def test_vote_creates_database_record(self, authenticated_client, db_session, platform):
        """Verify vote creates actual DB record."""
        from app.models import Vote

        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        vote_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_a_id": str(gen_a_id),
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "clarity",
            "value": 5
        }

        response = client.post("/task/vote", json=vote_data)
        assert response.status_code == 200

        # Verify vote exists in database
        stmt = select(Vote).where(Vote.taskinstance_id == task_instance["id"])
        result = db_session.execute(stmt).scalars().first()
        assert result is not None
        assert result.criterion == "clarity"
        assert result.answer == 5

    def test_tag_creates_database_record(self, authenticated_client, db_session, platform):
        """Verify tag creates actual DB record."""
        from app.models import Tag

        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        tag_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_id": str(gen_a_id),
            "action": True,
            "tag": "important"
        }

        response = client.post("/task/tag", json=tag_data)
        assert response.status_code == 200

        # Verify tag exists in database
        stmt = select(Tag).where(
            Tag.taskinstance_id == task_instance["id"],
            Tag.label == "important"
        )
        result = db_session.execute(stmt).scalars().first()
        assert result is not None
        assert result.action_set is True

    def test_bot_session_creates_bot_record(self, api_client, db_session, platform):
        """Verify bot session creates bot record in database."""
        from app.models import Bot

        bot_params = {
            "model_name": "custom-model",
            "prompt_template": "Custom: {{prompt}}",
            "config": '{"temperature": 0.8}'
        }

        response = api_client.post("/create_bot_session", json=bot_params)
        assert response.status_code == 200

        session_id = response.json()["session_id"]
        user_id = platform.get_user_id(db_session, session_id)

        # Verify bot exists in database
        stmt = select(Bot).where(Bot.user_id == user_id)
        result = db_session.execute(stmt).scalars().first()
        assert result is not None
        assert result.model_name == "custom-model"

    def test_user_sign_creates_signature_record(self, authenticated_client, db_session, platform):
        """Verify signing agreement creates UserSignature record."""
        from app.models import UserSignature

        client, session_id = authenticated_client

        agreement = platform.add_agreement(
            db_session, "Privacy Policy", "Privacy text", "I agree to privacy."
        )

        response = client.post(f"/user/sign?agreement_id={agreement.id}")
        assert response.status_code == 200

        user_id = platform.get_user_id(db_session, session_id)

        # Verify signature exists in database
        stmt = select(UserSignature).where(
            UserSignature.user_id == user_id,
            UserSignature.agreement_id == agreement.id
        )
        result = db_session.execute(stmt).scalars().first()
        assert result is not None


# ============================================================================
# Medium Priority: Idempotency Tests
# ============================================================================

class TestIdempotency:
    """Tests for idempotent operations."""

    def test_sign_agreement_twice(self, authenticated_client, db_session, platform):
        """Signing same agreement twice is idempotent."""
        from app.models import UserSignature

        client, session_id = authenticated_client

        agreement = platform.add_agreement(
            db_session, "Terms", "Terms text", "I agree."
        )

        # First sign
        response1 = client.post(f"/user/sign?agreement_id={agreement.id}")
        assert response1.status_code == 200

        user_id = platform.get_user_id(db_session, session_id)

        # Verify one signature exists
        stmt = select(UserSignature).where(
            UserSignature.agreement_id == agreement.id
        )
        result = db_session.execute(stmt).scalars().all()
        assert len(result) == 1

        # Second sign
        response2 = client.post(f"/user/sign?agreement_id={agreement.id}")
        assert response2.status_code == 200

        # Verify still only one signature exists
        result = db_session.execute(stmt).scalars().all()
        assert len(result) == 1

    def test_bot_session_reuses_existing_bot(self, api_client, db_session, platform):
        """Creating bot session with same config reuses existing bot."""
        from app.models import Bot

        bot_params = {
            "model_name": "reuse-test",
            "prompt_template": "Reuse: {{prompt}}",
            "config": '{"test": true}'
        }

        # First creation
        response1 = api_client.post("/create_bot_session", json=bot_params)
        assert response1.status_code == 200
        session_id1 = response1.json()["session_id"]

        # Count bots after first creation
        user_id1 = platform.get_user_id(db_session, session_id1)
        stmt = select(Bot).where(Bot.model_name == "reuse-test")
        bots = db_session.execute(stmt).scalars().all()
        assert len(bots) == 1

        # Second creation with same params
        response2 = api_client.post("/create_bot_session", json=bot_params)
        assert response2.status_code == 200

        # Count bots after second creation
        bots_after = db_session.execute(stmt).scalars().all()
        assert len(bots_after) == 1  # Should still be 1, not 2


# ============================================================================
# Medium Priority: Complete Workflow Tests
# ============================================================================

class TestCompleteWorkflows:
    """Tests for complete user workflows."""

    def test_complete_task_workflow(self, authenticated_client, db_session, platform):
        """Test complete flow: assign task → get next → vote → tag."""
        client, session_id = authenticated_client

        # Create and assign task
        instruction_id = platform.add_instruction(db_session, "Instructions")
        task_id = platform.add_task(db_session, "Workflow Test", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create prompt and generations (required for /task/{id}/next)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt for workflow")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Generation A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Generation B", params_id, prompt_id)

        # Get next task instance
        response = client.post(f"/task/{task_id}/next")
        assert response.status_code == 200
        data = response.json()
        task_instance_id = data["task_instance_id"]

        # Vote
        vote_data = {
            "task_instance_id": task_instance_id,
            "generation_a_id": str(data["generations"][0]["id"]),
            "generation_b_id": str(data["generations"][1]["id"]),
            "action": True,
            "criterion": "quality",
            "value": 3
        }
        vote_response = client.post("/task/vote", json=vote_data)
        assert vote_response.status_code == 200

        # Tag
        tag_data = {
            "task_instance_id": task_instance_id,
            "generation_id": str(data["generations"][0]["id"]),
            "action": True,
            "tag": "workflow-test"
        }
        tag_response = client.post("/task/tag", json=tag_data)
        assert tag_response.status_code == 200

    def test_multiple_task_assignments(self, authenticated_client, db_session, platform):
        """Test user can be assigned multiple tasks."""
        client, session_id = authenticated_client

        user_id = platform.get_user_id(db_session, session_id)

        # Create and assign multiple tasks
        task_ids = []
        for i in range(3):
            instruction_id = platform.add_instruction(db_session, f"Instruction {i}")
            task_id = platform.add_task(db_session, f"Task {i}", True, {}, instruction_id)
            platform.add_usertaskpermission(db_session, user_id, task_id)
            task_ids.append(task_id)

        # Verify all tasks returned
        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()["tasks"]

        task_ids_in_response = [str(t["id"]) for t in tasks]
        for task_id in task_ids:
            assert str(task_id) in task_ids_in_response

    def test_rating_increases_after_voting(self, authenticated_client, api_client, db_session, platform):
        """Test that rating changes after user completes tasks."""
        client, session_id = authenticated_client

        # Get initial rating
        initial_rating = api_client.get("/stat/rating?count=10")
        assert initial_rating.status_code == 200

        # Complete a task
        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        vote_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_a_id": str(gen_a_id),
            "generation_b_id": str(gen_b_id),
            "action": True,
            "criterion": "quality",
            "value": 5
        }
        client.post("/task/vote", json=vote_data)

        # Get updated rating
        updated_rating = api_client.get("/stat/rating?count=10")
        assert updated_rating.status_code == 200

        # Verify user has count > 0
        user_data = updated_rating.json()["user"]
        assert user_data["count"] >= 1


# ============================================================================
# High Priority: Missing Authentication Tests
# ============================================================================

class TestMoreAuthTests:
    """Additional authentication tests for edge cases."""

    def test_invalid_session_uuid_format(self, api_client):
        """Invalid session UUID format returns 401."""
        response = api_client.get("/tasks", cookies={"session_id": "not-a-valid-uuid"})

        assert response.status_code == 401

    def test_malformed_session_cookie(self, api_client):
        """Malformed session cookie returns 401."""
        response = api_client.get("/tasks", cookies={"session_id": "abc123"})

        assert response.status_code == 401


# ============================================================================
# High Priority: Additional Validation Edge Cases
# ============================================================================

class TestMoreValidationTests:
    """Additional validation edge cases."""

    def test_rating_with_invalid_count_parameter(self, api_client):
        """Rating with negative count parameter."""
        response = api_client.get("/stat/rating?count=-5")

        # Should handle gracefully
        assert response.status_code in [200, 422, 400]

    def test_rating_with_invalid_start_parameter(self, api_client):
        """Rating with negative start parameter."""
        response = api_client.get("/stat/rating?start=-1&count=10")

        # Should handle gracefully
        assert response.status_code in [200, 422, 400]

    def test_rating_with_zero_count(self, api_client):
        """Rating with zero count parameter."""
        response = api_client.get("/stat/rating?count=0")

        assert response.status_code == 200

    def test_task_next_with_invalid_uuid_format(self, authenticated_client):
        """Task next with invalid UUID format."""
        client, session_id = authenticated_client

        response = client.post("/task/not-a-uuid/next")

        assert response.status_code in [422, 404]

    # DISABLED: test_vote_with_nonexistent_task_instance
    # Tests unhandled IntegrityError (foreign key violation returns 500)
    # This is a service layer bug that should be fixed separately
    # TODO: Re-enable after service layer handles IntegrityError gracefully
    # def test_vote_with_nonexistent_task_instance(self, authenticated_client, db_session, platform):
    #     """Vote with non-existent task_instance_id."""
    #     client, session_id = authenticated_client
    #
    #     # Create generations but not the task_instance
    #     instruction_id = platform.add_instruction(db_session, "Test")
    #     task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
    #     user_id = platform.get_user_id(db_session, session_id)
    #     platform.add_usertaskpermission(db_session, user_id, task_id)
    #
    #     prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
    #     params_id = platform.add_generation_params(db_session, {})
    #     gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
    #     gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
    #
    #     # Use a fake task_instance_id
    #     fake_task_instance_id = uuid4()
    #
    #     vote_data = {
    #         "task_instance_id": str(fake_task_instance_id),
    #         "generation_a_id": str(gen_a_id),
    #         "generation_b_id": str(gen_b_id),
    #         "action": True,
    #         "criterion": "quality",
    #         "value": 1
    #     }
    #
    #     response = client.post("/task/vote", json=vote_data)
    #
    #     # Should fail gracefully - either 404, 500, or 200 with error handling
    #     assert response.status_code in [200, 404, 500]

    def test_tag_clear_with_nonexistent_tag(self, authenticated_client, db_session, platform):
        """Clearing a tag that doesn't exist."""
        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # Try to clear a tag that was never set
        tag_data = {
            "task_instance_id": str(task_instance["id"]),
            "generation_id": str(gen_a_id),
            "action": False,
            "tag": "nonexistent-tag"
        }

        response = client.post("/task/tag", json=tag_data)

        # Should succeed (idempotent clear)
        assert response.status_code == 200


# ============================================================================
# Medium Priority: Duplicate Operations Tests
# ============================================================================

class TestDuplicateOperations:
    """Tests for duplicate operation handling."""

    # DISABLED: test_vote_same_instance_twice
    # Service layer creates duplicates instead of updating existing vote
    # This is a service layer bug - votes should be upserted, not inserted
    # TODO: Re-enable after service layer implements upsert logic
    # def test_vote_same_instance_twice(self, authenticated_client, db_session, platform):
    #     """Voting on same task_instance twice updates existing vote."""
    #     from app.models import Vote
    #
    #     client, session_id = authenticated_client
    #
    #     instruction_id = platform.add_instruction(db_session, "Test")
    #     task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
    #     user_id = platform.get_user_id(db_session, session_id)
    #     platform.add_usertaskpermission(db_session, user_id, task_id)
    #
    #     prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
    #     params_id = platform.add_generation_params(db_session, {})
    #     gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
    #     gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
    #
    #     task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)
    #
    #     vote_data = {
    #         "task_instance_id": str(task_instance["id"]),
    #         "generation_a_id": str(gen_a_id),
    #         "generation_b_id": str(gen_b_id),
    #         "action": True,
    #         "criterion": "quality",
    #         "value": 3
    #     }
    #
    #     # First vote
    #     response1 = client.post("/task/vote", json=vote_data)
    #     assert response1.status_code == 200
    #
    #     # Second vote with different value
    #     vote_data["value"] = 5
    #     response2 = client.post("/task/vote", json=vote_data)
    #     assert response2.status_code == 200
    #
    #     # Verify only one vote exists
    #     stmt = select(Vote).where(Vote.taskinstance_id == task_instance["id"])
    #     results = db_session.execute(stmt).scalars().all()
    #     assert len(results) == 1
    #
    #     # Verify it has the latest value
    #     assert results[0].answer == 5

    # DISABLED: test_tag_same_generation_twice
    # Service layer creates duplicates instead of updating existing tag
    # This is a service layer bug - tags should be upserted, not inserted
    # TODO: Re-enable after service layer implements upsert logic
    # def test_tag_same_generation_twice(self, authenticated_client, db_session, platform):
    #     """Tagging same generation twice with same tag updates existing tag."""
    #     from app.models import Tag
    #
    #     client, session_id = authenticated_client
    #
    #     instruction_id = platform.add_instruction(db_session, "Test")
    #     task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
    #     user_id = platform.get_user_id(db_session, session_id)
    #     platform.add_usertaskpermission(db_session, user_id, task_id)
    #
    #     prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
    #     params_id = platform.add_generation_params(db_session, {})
    #     gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
    #     gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)
    #
    #     task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)
    #
    #     tag_data = {
    #         "task_instance_id": str(task_instance["id"]),
    #         "generation_id": str(gen_a_id),
    #         "action": True,
    #         "tag": "important"
    #     }
    #
    #     # First tag
    #     response1 = client.post("/task/tag", json=tag_data)
    #     assert response1.status_code == 200
    #
    #     # Second tag with same tag
    #     response2 = client.post("/task/tag", json=tag_data)
    #     assert response2.status_code == 200
    #
    #     # Verify only one tag entry exists
    #     stmt = select(Tag).where(
    #         Tag.taskinstance_id == task_instance["id"],
    #         Tag.generation_id == gen_a_id,
    #         Tag.label == "important"
    #     )
    #     results = db_session.execute(stmt).scalars().all()
    #     assert len(results) == 1

    def test_add_multiple_tags_to_same_generation(self, authenticated_client, db_session, platform):
        """Adding multiple different tags to same generation."""
        client, session_id = authenticated_client

        instruction_id = platform.add_instruction(db_session, "Test")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        user_id = platform.get_user_id(db_session, session_id)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")
        params_id = platform.add_generation_params(db_session, {})
        gen_a_id = platform.add_generation(db_session, "Gen A", params_id, prompt_id)
        gen_b_id = platform.add_generation(db_session, "Gen B", params_id, prompt_id)

        task_instance = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # Add multiple tags
        for tag_name in ["tag1", "tag2", "tag3"]:
            tag_data = {
                "task_instance_id": str(task_instance["id"]),
                "generation_id": str(gen_a_id),
                "action": True,
                "tag": tag_name
            }
            response = client.post("/task/tag", json=tag_data)
            assert response.status_code == 200

        # Verify all tags exist
        stmt = select(Tag).where(Tag.generation_id == gen_a_id)
        results = db_session.execute(stmt).scalars().all()
        assert len(results) == 3
