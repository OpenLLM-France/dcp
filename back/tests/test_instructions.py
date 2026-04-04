import pytest
from app.models import Instruction, Task


def test_add_instruction_creates(db_session, platform):
    """`add_instruction` creates a new instruction."""
    instruction_id = platform.add_instruction(db_session, "Test instruction text")
    
    assert isinstance(instruction_id, int)
    instruction = db_session.query(Instruction).filter_by(id=instruction_id).one()
    assert instruction.text == "Test instruction text"


def test_get_instruction_for_task_success(db_session, platform):
    """`get_instruction_for_task` retrieves instruction for a task."""
    instruction_id = platform.add_instruction(db_session, "Instruction for task")
    task_id = platform.add_task(
        db_session, 
        "Task with instruction", 
        True, 
        {}, 
        instruction_id
    )
    
    result = platform.get_instruction_for_task(db_session, task_id)
    
    assert result['id'] == instruction_id
    assert result['text'] == "Instruction for task"


def test_get_instruction_for_task_no_task(db_session, platform):
    """`get_instruction_for_task` raises error when task not found."""
    # Create an instruction but no task
    instruction_id = platform.add_instruction(db_session, "Standalone instruction")
    
    # Try to get instruction for non-existent task (use UUID format)
    with pytest.raises(Exception):
        platform.get_instruction_for_task(db_session, "00000000-0000-0000-0000-000000000000")
