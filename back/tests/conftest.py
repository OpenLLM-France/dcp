import os
import subprocess
import time
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.service import DataCollectionPlatform
from app.models import (
    Task, Instruction, Prompt, Generation, GenerationParams, 
    TaskInstance, GenerationView, UserTaskPermission, User, Bot,
    Agreement, UserSignature
)

POSTGRES_CONTAINER_NAME = "test-postgres-dcp"
POSTGRES_PASSWORD = "test123"
POSTGRES_DB = "testdb"
POSTGRES_USER = "postgres"
POSTGRES_PORT = 5432

XDG_RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR", "/run/user/1002")
DOCKER_HOST = os.environ.get("DOCKER_HOST", "unix:///run/user/1002/podman/podman.sock")


def _get_connection_url():
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"


def _use_external_database():
    """Check if we should use an external database (e.g., GitHub Actions service container)."""
    return os.environ.get("DATABASE_URL") is not None


def _start_postgres():
    """Start PostgreSQL container using podman."""
    # Stop and remove existing container if any
    subprocess.run(
        ["podman", "stop", POSTGRES_CONTAINER_NAME],
        env={"XDG_RUNTIME_DIR": XDG_RUNTIME_DIR, "DOCKER_HOST": DOCKER_HOST},
        capture_output=True
    )
    subprocess.run(
        ["podman", "rm", POSTGRES_CONTAINER_NAME],
        env={"XDG_RUNTIME_DIR": XDG_RUNTIME_DIR, "DOCKER_HOST": DOCKER_HOST},
        capture_output=True
    )

    # Start new container with host network mode
    result = subprocess.run(
        [
            "podman", "run", "-d",
            "--name", POSTGRES_CONTAINER_NAME,
            "--network", "host",
            "-e", f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
            "-e", f"POSTGRES_DB={POSTGRES_DB}",
            "-e", f"POSTGRES_USER={POSTGRES_USER}",
            "docker.io/library/postgres:15"
        ],
        env={"XDG_RUNTIME_DIR": XDG_RUNTIME_DIR, "DOCKER_HOST": DOCKER_HOST},
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to start PostgreSQL container: {result.stderr}")

    # Wait for PostgreSQL to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            engine = create_engine(_get_connection_url())
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("PostgreSQL container failed to become ready")


def _stop_postgres():
    """Stop and remove PostgreSQL container."""
    subprocess.run(
        ["podman", "stop", POSTGRES_CONTAINER_NAME],
        env={"XDG_RUNTIME_DIR": XDG_RUNTIME_DIR, "DOCKER_HOST": DOCKER_HOST},
        capture_output=True
    )
    subprocess.run(
        ["podman", "rm", POSTGRES_CONTAINER_NAME],
        env={"XDG_RUNTIME_DIR": XDG_RUNTIME_DIR, "DOCKER_HOST": DOCKER_HOST},
        capture_output=True
    )


@pytest.fixture(scope="session")
def postgres_engine():
    """Start PostgreSQL container for the test session, or use external database if DATABASE_URL is set."""
    if _use_external_database():
        engine = create_engine(os.environ["DATABASE_URL"])
        yield engine
    else:
        engine = _start_postgres()
        yield engine
        _stop_postgres()


@pytest.fixture(autouse=True)
def setup_database(postgres_engine):
    """Drop and recreate tables before each test for clean state."""
    # Drop all tables first (cleanup from previous test)
    Base.metadata.drop_all(postgres_engine)
    Base.metadata.create_all(postgres_engine)

    yield  # Test runs here

    # Cleanup after test
    Base.metadata.drop_all(postgres_engine)


@pytest.fixture
def db_session(postgres_engine):
    """Provide a database session for each test."""
    Session = sessionmaker(bind=postgres_engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def platform():
    """Instantiate the service class (stateless)."""
    return DataCollectionPlatform()


@pytest.fixture
def seeded_instruction(db_session, platform):
    """Create an instruction for task tests."""
    instruction_id = platform.add_instruction(db_session, "Test instruction for tasks")
    return db_session.query(Instruction).filter_by(id=instruction_id).one()


@pytest.fixture
def seeded_task(db_session, platform, seeded_instruction):
    """Create a task with instruction for tests."""
    task_id = platform.add_task(
        db_session, 
        "Test Task", 
        True, 
        {"test": "data"}, 
        seeded_instruction.id
    )
    return {
        'task_id': task_id,
        'task': db_session.query(Task).filter_by(id=task_id).one()
    }


@pytest.fixture
def seeded_prompts(db_session, platform, seeded_task):
    """Create multiple prompts for a task."""
    prompts = []
    for i in range(5):
        prompt_id = platform.add_prompt(db_session, seeded_task['task_id'], f"Test prompt {i}")
        prompts.append(db_session.query(Prompt).filter_by(id=prompt_id).one())
    return prompts


@pytest.fixture
def seeded_generations(db_session, platform, seeded_prompts):
    """Create generations for the first 3 prompts."""
    params_id = platform.add_generation_params(db_session, {"temperature": 0.7, "max_tokens": 100})
    generations = []
    for prompt in seeded_prompts[:3]:
        for j in range(2):
            gen_id = platform.add_generation(
                db_session, 
                f"Generation {j} for prompt {prompt.id}", 
                params_id, 
                prompt.id
            )
            generations.append(db_session.query(Generation).filter_by(id=gen_id).one())
    return generations


@pytest.fixture
def complete_task_setup(db_session, platform, seeded_task, seeded_prompts, seeded_generations):
    """Full setup for task instance tests with user and permissions."""
    session_id, user_id = platform.add_user(db_session)
    platform.add_usertaskpermission(db_session, user_id, seeded_task['task_id'])
    return {
        'session_id': session_id,
        'user_id': user_id,
        'task_id': seeded_task['task_id'],
        'task': seeded_task['task'],
        'prompts': seeded_prompts,
        'generations': seeded_generations
    }


@pytest.fixture
def test_user(db_session, platform):
    """Create a test user with session."""
    session_id, user_id = platform.add_user(db_session)
    return {'session_id': session_id, 'user_id': user_id}


@pytest.fixture
def authorized_user(db_session, platform, seeded_task):
    """Create a user with permission to a specific task."""
    session_id, user_id = platform.add_user(db_session)
    platform.add_usertaskpermission(db_session, user_id, seeded_task['task_id'])
    return {'session_id': session_id, 'user_id': user_id, 'task_id': seeded_task['task_id']}


@pytest.fixture
def seeded_bot(db_session, platform, test_user):
    """Create a test bot for bot management tests using create_bot_session."""
    session_id = platform.create_bot_session(
        db_session,
        "test-model-v1",
        "Here is the response: {{prompt}}",
        {"temperature": 0.7}
    )
    # Get the user_id from the session and then bot info
    user_id = platform.get_user_id(db_session, session_id)
    bot_info = platform.get_bot_info(db_session, user_id)
    return {
        'session_id': session_id,
        'user_id': user_id,
        'bot_info': bot_info
    }


@pytest.fixture
def seeded_agreement(db_session, platform):
    """Create a test agreement for agreement tests."""
    agreement = platform.add_agreement(
        db_session,
        "Test Agreement",
        "A test agreement for testing",
        "I agree to the test terms and conditions."
    )
    return agreement


@pytest.fixture
def user_with_agreement(db_session, platform, seeded_agreement):
    """Create a user who has signed an agreement."""
    session_id, user_id = platform.add_user(db_session)
    platform.record_agreement(db_session, session_id, seeded_agreement.id)
    return {
        'session_id': session_id,
        'user_id': user_id,
        'agreement_id': seeded_agreement.id
    }


@pytest.fixture
def task_instance_for_user(db_session, platform, complete_task_setup):
    """Create a task instance for a user with prompts and generations."""
    session_id = complete_task_setup['session_id']
    user_id = complete_task_setup['user_id']
    task_id = complete_task_setup['task_id']
    
    task_instance = platform.get_task_instance_for_user(
        db_session, str(task_id), user_id
    )
    
    return {
        'task_instance': task_instance,
        'user_id': user_id,
        'session_id': session_id,
        'task_id': task_id
    }
