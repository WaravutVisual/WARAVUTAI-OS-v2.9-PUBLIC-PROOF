from app.g21_db import G21Database
from app.queue import JobQueue
from app.retry import RetryPolicy


# G23-001
def test_g23_001_g21_database_remains_available():
    db = G21Database()

    assert db.path.exists()


# G23-002
def test_g23_002_queue_can_enqueue_and_dequeue():
    queue = JobQueue()

    job_id = "G23-QUEUE-001"

    queue.enqueue(job_id)

    assert queue.dequeue(timeout=0.1) == job_id


# G23-003
def test_g23_003_retry_policy_default_remains_two():
    policy = RetryPolicy()

    assert policy.max_attempts == 2


# G23-004
def test_g23_004_retry_boundary_remains_stable():
    policy = RetryPolicy()

    assert policy.can_retry(0) is True
    assert policy.can_retry(1) is True
    assert policy.can_retry(2) is False
