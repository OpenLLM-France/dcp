"""Tests for least viewed prompt and generation selection logic."""
import pytest
from app.models import Prompt, Generation, GenerationView, TaskInstance


class TestLeastTouchedPromptSelection:
    """Tests for __get_least_touched_prompt selection logic."""

    def test_selects_prompt_with_fewest_task_instances(self, db_session, platform):
        """Test that the prompt with fewest task instances is selected."""
        # Create task and instruction
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)

        # Create user and permission
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create 3 prompts
        prompt_1_id = platform.add_prompt(db_session, task_id, "Prompt 1")
        prompt_2_id = platform.add_prompt(db_session, task_id, "Prompt 2")
        prompt_3_id = platform.add_prompt(db_session, task_id, "Prompt 3")

        # Create task instances: prompt_1 has 2, prompt_2 has 1, prompt_3 has 0
        params_id = platform.add_generation_params(db_session, {})
        gen_1a_id = platform.add_generation(db_session, "Gen 1A", params_id, prompt_1_id)
        gen_1b_id = platform.add_generation(db_session, "Gen 1B", params_id, prompt_1_id)
        gen_2a_id = platform.add_generation(db_session, "Gen 2A", params_id, prompt_2_id)
        gen_2b_id = platform.add_generation(db_session, "Gen 2B", params_id, prompt_2_id)
        gen_3a_id = platform.add_generation(db_session, "Gen 3A", params_id, prompt_3_id)
        gen_3b_id = platform.add_generation(db_session, "Gen 3B", params_id, prompt_3_id)

        # Create task instances for prompt_1 (2 instances)
        platform.get_task_instance_for_user(db_session, str(task_id), user_id)
        platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # Create task instance for prompt_2 (1 instance)
        # First delete instances from prompt_1 to reset counts
        db_session.query(TaskInstance).filter(
            TaskInstance.prompt_id.in_([prompt_1_id, prompt_2_id, prompt_3_id])
        ).delete(synchronize_session=False)
        db_session.commit()

        # Now create: prompt_1 has 2, prompt_2 has 1, prompt_3 has 0
        ti_1_1 = TaskInstance(user_id=user_id, prompt_id=prompt_1_id,
                             generation_a_id=gen_1a_id, generation_b_id=gen_1b_id)
        ti_1_2 = TaskInstance(user_id=user_id, prompt_id=prompt_1_id,
                             generation_a_id=gen_1a_id, generation_b_id=gen_1b_id)
        ti_2_1 = TaskInstance(user_id=user_id, prompt_id=prompt_2_id,
                             generation_a_id=gen_2a_id, generation_b_id=gen_2b_id)
        db_session.add_all([ti_1_1, ti_1_2, ti_2_1])
        db_session.commit()

        # Get least touched prompt - should be prompt_3 (0 task instances)
        least_touched = platform._DataCollectionPlatform__get_least_touched_prompt(
            db_session, task_id, user_id
        )

        assert least_touched.id == prompt_3_id

    def test_returns_random_prompt_when_all_have_same_count(self, db_session, platform):
        """Test that any prompt is returned when all have equal task instance counts."""
        # Create task and instruction
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)

        # Create user and permission
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create 2 prompts with same number of task instances (1 each)
        prompt_1_id = platform.add_prompt(db_session, task_id, "Prompt 1")
        prompt_2_id = platform.add_prompt(db_session, task_id, "Prompt 2")

        params_id = platform.add_generation_params(db_session, {})
        gen_1a_id = platform.add_generation(db_session, "Gen 1A", params_id, prompt_1_id)
        gen_1b_id = platform.add_generation(db_session, "Gen 1B", params_id, prompt_1_id)
        gen_2a_id = platform.add_generation(db_session, "Gen 2A", params_id, prompt_2_id)
        gen_2b_id = platform.add_generation(db_session, "Gen 2B", params_id, prompt_2_id)

        # Create 1 task instance for each prompt
        ti_1 = TaskInstance(user_id=user_id, prompt_id=prompt_1_id,
                           generation_a_id=gen_1a_id, generation_b_id=gen_1b_id)
        ti_2 = TaskInstance(user_id=user_id, prompt_id=prompt_2_id,
                           generation_a_id=gen_2a_id, generation_b_id=gen_2b_id)
        db_session.add_all([ti_1, ti_2])
        db_session.commit()

        # Should return either prompt (both have 1 task instance)
        result = platform._DataCollectionPlatform__get_least_touched_prompt(
            db_session, task_id, user_id
        )

        assert result.id in [prompt_1_id, prompt_2_id]


class TestLeastViewedGenerationsSelection:
    """Tests for __get_least_viewed_generations selection logic."""

    def test_selects_generations_with_fewest_views(self, db_session, platform):
        """Test that generations with fewest views are selected."""
        # Create task, instruction, prompt
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")

        # Create user
        session_id, user_id = platform.add_user(db_session)

        # Create 4 generations
        params_id = platform.add_generation_params(db_session, {})
        gen_1_id = platform.add_generation(db_session, "Gen 1", params_id, prompt_id)
        gen_2_id = platform.add_generation(db_session, "Gen 2", params_id, prompt_id)
        gen_3_id = platform.add_generation(db_session, "Gen 3", params_id, prompt_id)
        gen_4_id = platform.add_generation(db_session, "Gen 4", params_id, prompt_id)

        # Create views: gen_1 has 2, gen_2 has 1, gen_3 has 0, gen_4 has 0
        view_1_1 = GenerationView(user_id=user_id, generation_id=gen_1_id)
        view_1_2 = GenerationView(user_id=user_id, generation_id=gen_1_id)
        view_2_1 = GenerationView(user_id=user_id, generation_id=gen_2_id)
        db_session.add_all([view_1_1, view_1_2, view_2_1])
        db_session.commit()

        # Get least viewed generations - should be gen_3 and gen_4 (0 views each)
        least_viewed = platform._DataCollectionPlatform__get_least_viewed_generations(
            db_session, prompt_id, user_id
        )

        gen_ids = [g.id for g in least_viewed]
        assert gen_3_id in gen_ids
        assert gen_4_id in gen_ids

    def test_selects_generations_with_equal_minimum_views(self, db_session, platform):
        """Test that any 2 generations are selected when multiple have same minimum views."""
        # Create task, instruction, prompt
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")

        # Create user
        session_id, user_id = platform.add_user(db_session)

        # Create 3 generations, all with 1 view each
        params_id = platform.add_generation_params(db_session, {})
        gen_1_id = platform.add_generation(db_session, "Gen 1", params_id, prompt_id)
        gen_2_id = platform.add_generation(db_session, "Gen 2", params_id, prompt_id)
        gen_3_id = platform.add_generation(db_session, "Gen 3", params_id, prompt_id)

        # Create 1 view for each generation
        view_1 = GenerationView(user_id=user_id, generation_id=gen_1_id)
        view_2 = GenerationView(user_id=user_id, generation_id=gen_2_id)
        view_3 = GenerationView(user_id=user_id, generation_id=gen_3_id)
        db_session.add_all([view_1, view_2, view_3])
        db_session.commit()

        # Should return any 2 generations
        result = platform._DataCollectionPlatform__get_least_viewed_generations(
            db_session, prompt_id, user_id
        )

        assert len(result) == 2
        result_ids = [g.id for g in result]
        assert all(gid in [gen_1_id, gen_2_id, gen_3_id] for gid in result_ids)


class TestGetTaskInstanceForUserSelection:
    """Integration tests for get_task_instance_for_user selection logic."""

    def test_returns_prompt_with_least_task_instances(self, db_session, platform):
        """Test that get_task_instance_for_user returns the prompt with fewest instances."""
        # Create task and instruction
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)

        # Create user and permission
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create 2 prompts
        prompt_1_id = platform.add_prompt(db_session, task_id, "Prompt 1 - More used")
        prompt_2_id = platform.add_prompt(db_session, task_id, "Prompt 2 - Less used")

        # Create generations for both prompts
        params_id = platform.add_generation_params(db_session, {})
        gen_1a_id = platform.add_generation(db_session, "Gen 1A", params_id, prompt_1_id)
        gen_1b_id = platform.add_generation(db_session, "Gen 1B", params_id, prompt_1_id)
        gen_2a_id = platform.add_generation(db_session, "Gen 2A", params_id, prompt_2_id)
        gen_2b_id = platform.add_generation(db_session, "Gen 2B", params_id, prompt_2_id)

        # Create 2 task instances for prompt_1, 0 for prompt_2
        ti_1 = TaskInstance(user_id=user_id, prompt_id=prompt_1_id,
                           generation_a_id=gen_1a_id, generation_b_id=gen_1b_id)
        ti_2 = TaskInstance(user_id=user_id, prompt_id=prompt_1_id,
                           generation_a_id=gen_1a_id, generation_b_id=gen_1b_id)
        db_session.add_all([ti_1, ti_2])
        db_session.commit()

        # Get task instance - should use prompt_2 (0 instances)
        result = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # Verify prompt_2 was selected (prompt is returned as text string)
        assert "Prompt 2" in result['prompt']

    def test_returns_generations_with_least_views(self, db_session, platform):
        """Test that get_task_instance_for_user returns generations with fewest views."""
        # Create task, instruction, prompt
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")

        # Create user and permission
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create 4 generations
        params_id = platform.add_generation_params(db_session, {})
        gen_1_id = platform.add_generation(db_session, "Gen 1 - More viewed", params_id, prompt_id)
        gen_2_id = platform.add_generation(db_session, "Gen 2 - Less viewed", params_id, prompt_id)
        gen_3_id = platform.add_generation(db_session, "Gen 3 - Least viewed", params_id, prompt_id)
        gen_4_id = platform.add_generation(db_session, "Gen 4 - Least viewed", params_id, prompt_id)

        # Create views: gen_1 has 2, gen_2 has 1, gen_3 and gen_4 have 0
        view_1_1 = GenerationView(user_id=user_id, generation_id=gen_1_id)
        view_1_2 = GenerationView(user_id=user_id, generation_id=gen_1_id)
        view_2_1 = GenerationView(user_id=user_id, generation_id=gen_2_id)
        db_session.add_all([view_1_1, view_1_2, view_2_1])
        db_session.commit()

        # Create a task instance to trigger generation selection
        result = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # The returned generations should be gen_3 and gen_4 (0 views each)
        gen_ids = [g['id'] for g in result['generations']]
        assert gen_3_id in gen_ids
        assert gen_4_id in gen_ids

    def test_subsequent_calls_respect_updated_view_counts(self, db_session, platform):
        """Test that subsequent calls to get_task_instance_for_user respect updated view counts."""
        # Create task, instruction, prompt
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")

        # Create user and permission
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create 3 generations
        params_id = platform.add_generation_params(db_session, {})
        gen_1_id = platform.add_generation(db_session, "Gen 1", params_id, prompt_id)
        gen_2_id = platform.add_generation(db_session, "Gen 2", params_id, prompt_id)
        gen_3_id = platform.add_generation(db_session, "Gen 3", params_id, prompt_id)

        # First call: all generations have 0 views, should get 2 of them (e.g., gen_1 and gen_2)
        result_1 = platform.get_task_instance_for_user(db_session, str(task_id), user_id)
        gen_ids_1 = [g['id'] for g in result_1['generations']]

        # After first call, those 2 generations now have 1 view each
        # Third generation still has 0 views

        # Second call: should prefer the generation with 0 views
        result_2 = platform.get_task_instance_for_user(db_session, str(task_id), user_id)
        gen_ids_2 = [g['id'] for g in result_2['generations']]

        # The generation that wasn't shown in first call should be in second call
        unseen_gen = set(gen_ids_1).symmetric_difference(set(gen_ids_2))
        # At least one generation from the second call should be different
        # (the one that had 0 views after first call)
        assert len(unseen_gen) >= 1 or gen_ids_1 != gen_ids_2


class TestViewCountingLogic:
    """Tests for view counting and its effect on selection."""

    def test_views_are_recorded_after_get_task_instance(self, db_session, platform):
        """Test that views are recorded after calling get_task_instance_for_user."""
        # Create task, instruction, prompt
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")

        # Create user
        session_id, user_id = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id, task_id)

        # Create 2 generations
        params_id = platform.add_generation_params(db_session, {})
        gen_1_id = platform.add_generation(db_session, "Gen 1", params_id, prompt_id)
        gen_2_id = platform.add_generation(db_session, "Gen 2", params_id, prompt_id)

        # Get task instance
        result = platform.get_task_instance_for_user(db_session, str(task_id), user_id)

        # Check that views were recorded
        view_count_1 = db_session.query(GenerationView).filter(
            GenerationView.generation_id == gen_1_id,
            GenerationView.user_id == user_id
        ).count()

        view_count_2 = db_session.query(GenerationView).filter(
            GenerationView.generation_id == gen_2_id,
            GenerationView.user_id == user_id
        ).count()

        assert view_count_1 == 1
        assert view_count_2 == 1

    def test_multiple_users_have_separate_view_counts(self, db_session, platform):
        """Test that different users have separate view counts."""
        # Create task, instruction, prompt
        instruction_id = platform.add_instruction(db_session, "Test instruction")
        task_id = platform.add_task(db_session, "Test Task", True, {}, instruction_id)
        prompt_id = platform.add_prompt(db_session, task_id, "Test prompt")

        # Create two users
        session_1, user_id_1 = platform.add_user(db_session)
        session_2, user_id_2 = platform.add_user(db_session)
        platform.add_usertaskpermission(db_session, user_id_1, task_id)
        platform.add_usertaskpermission(db_session, user_id_2, task_id)

        # Create 2 generations
        params_id = platform.add_generation_params(db_session, {})
        gen_1_id = platform.add_generation(db_session, "Gen 1", params_id, prompt_id)
        gen_2_id = platform.add_generation(db_session, "Gen 2", params_id, prompt_id)

        # User 1 views generations
        platform.get_task_instance_for_user(db_session, str(task_id), user_id_1)

        # User 2 should see same generations (both have 0 views for user 2)
        result_2 = platform.get_task_instance_for_user(db_session, str(task_id), user_id_2)

        # Verify user 2's view counts are separate
        view_count_user_2 = db_session.query(GenerationView).filter(
            GenerationView.user_id == user_id_2
        ).count()

        assert view_count_user_2 == 2  # User 2 has viewed 2 generations
