"""Tests for generation and generation params management."""
import pytest
from app.models import Generation, GenerationParams


class TestGenerationParams:
    """Tests for generation parameters."""

    def test_add_generation_params_creates_params(self, db_session, platform):
        """Test that add_generation_params creates parameters."""
        params_data = {"temperature": 0.7, "max_tokens": 100, "top_p": 0.9}
        params_id = platform.add_generation_params(db_session, params_data)
        
        params = db_session.get(GenerationParams, params_id)
        assert params is not None
        assert params.params == params_data

    def test_add_generation_params_with_empty_dict(self, db_session, platform):
        """Test adding empty generation parameters."""
        params_id = platform.add_generation_params(db_session, {})
        
        params = db_session.get(GenerationParams, params_id)
        assert params.params == {}

    def test_add_generation_params_generates_int_id(self, db_session, platform):
        """Test that generation params get integer IDs."""
        params_id = platform.add_generation_params(db_session, {"test": "value"})
        
        assert isinstance(params_id, int)

    def test_add_generation_params_with_complex_json(self, db_session, platform):
        """Test adding complex JSON parameters."""
        params_data = {
            "temperature": 0.7,
            "stop_sequences": ["\n\n", "END"],
            "metadata": {"version": "1.0", "model": "test"}
        }
        params_id = platform.add_generation_params(db_session, params_data)
        
        params = db_session.get(GenerationParams, params_id)
        assert params.params == params_data

    def test_find_generation_params_exists(self, db_session, platform):
        """Test finding generation params that exist."""
        params_data = {"temperature": 0.5}
        params_id = platform.add_generation_params(db_session, params_data)
        
        result = platform.find_generation_params(db_session, params_data)
        
        assert result is not None
        assert result['id'] == params_id

    def test_find_generation_params_not_exists(self, db_session, platform):
        """Test finding generation params that don't exist."""
        result = platform.find_generation_params(db_session, {"temperature": 0.99})
        
        assert result is None

    def test_add_generation_params_with_json_string(self, db_session, platform):
        """Test adding generation params from JSON string."""
        params_json = '{"temperature": 0.8, "max_tokens": 200}'
        params_id = platform.add_generation_params(db_session, params_json)
        
        params = db_session.get(GenerationParams, params_id)
        assert params is not None
        assert params.params == {"temperature": 0.8, "max_tokens": 200}


class TestGenerationCreation:
    """Tests for generation creation."""

    def test_add_generation_creates_generation(self, db_session, platform, seeded_prompts):
        """Test that add_generation creates a generation."""
        params_id = platform.add_generation_params(db_session, {"temperature": 0.7})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        generation_id = platform.add_generation(db_session, "Test generation text", params_id, prompt_id)
        
        assert generation_id is not None
        generation = db_session.get(Generation, generation_id)
        assert generation is not None
        assert generation.text == "Test generation text"
        assert generation.params_id == params_id
        assert generation.prompt_id == prompt_id

    def test_add_generation_generates_uuid(self, db_session, platform, seeded_prompts):
        """Test that add_generation generates a UUID."""
        params_id = platform.add_generation_params(db_session, {})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        generation_id = platform.add_generation(db_session, "Gen", params_id, prompt_id)
        
        # Should be a UUID (string or UUID object)
        import uuid
        assert generation_id is not None
        uuid.UUID(str(generation_id))

    def test_add_generation_with_empty_text(self, db_session, platform, seeded_prompts):
        """Test adding generation with empty text."""
        params_id = platform.add_generation_params(db_session, {})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        generation_id = platform.add_generation(db_session, "", params_id, prompt_id)
        
        generation = db_session.get(Generation, generation_id)
        assert generation.text == ""

    def test_add_multiple_generations_for_prompt(self, db_session, platform, seeded_prompts):
        """Test adding multiple generations to same prompt."""
        params_id = platform.add_generation_params(db_session, {})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        gen_ids = []
        for i in range(3):
            gen_id = platform.add_generation(db_session, f"Generation {i}", params_id, prompt_id)
            gen_ids.append(gen_id)
        
        generations = db_session.query(Generation).filter(
            Generation.prompt_id == prompt_id
        ).all()
        
        assert len(generations) == 3
        assert len(set(gen_ids)) == 3


class TestGenerationRetrieval:
    """Tests for retrieving generations."""

    def test_get_generations(self, db_session, platform, seeded_generations):
        """Test getting all generations."""
        generations = platform.get_generations(db_session)
        assert len(generations) == 6

    def test_get_generations_for_prompt(self, db_session, platform, seeded_prompts, seeded_generations):
        """Test getting all generations for a prompt."""
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        generations = platform.get_generations_for_prompt(db_session, prompt_id)
        
        assert len(generations) == 2
        assert all(g['text'] is not None for g in generations)

    def test_get_generations_for_prompt_empty(self, db_session, platform, seeded_prompts):
        """Test getting generations for prompt with none."""
        prompt_with_no_gens = seeded_prompts[-1]
        prompt_id = prompt_with_no_gens['id'] if isinstance(prompt_with_no_gens, dict) else prompt_with_no_gens.id
        generations = platform.get_generations_for_prompt(db_session, prompt_id)
        
        assert len(generations) == 0

    def test_find_generation_exists(self, db_session, platform, seeded_prompts):
        """Test finding a generation that exists."""
        params_id = platform.add_generation_params(db_session, {})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        platform.add_generation(db_session, "Find me", params_id, prompt_id)
        
        result = platform.find_generation(db_session, "Find me", params_id, prompt_id)
        
        assert result is not None
        assert result['text'] == "Find me"

    def test_find_generation_not_exists(self, db_session, platform, seeded_prompts):
        """Test finding a generation that doesn't exist."""
        params_id = platform.add_generation_params(db_session, {})
        prompt = seeded_prompts[0]
        prompt_id = prompt['id'] if isinstance(prompt, dict) else prompt.id
        
        result = platform.find_generation(db_session, "Non Existent", params_id, prompt_id)
        
        assert result is None
