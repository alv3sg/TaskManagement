import uuid
from datetime import datetime, timezone, timedelta
import pytest
from src.auth.domain.entities import Inbox, InboxStatus, UserId


@pytest.fixture
def sample_inbox():
    user_id = UserId(str(uuid.uuid4()))
    return Inbox(
        id=uuid.uuid4(),
        user_id=user_id,
        description="Test Inbox"
    )


def test_inbox_initialization(sample_inbox):
    """Test that Inbox is properly initialized with default values."""
    assert sample_inbox.description == "Test Inbox"
    assert sample_inbox.status == InboxStatus.ACTIVE
    assert isinstance(sample_inbox.created_at, datetime)
    assert sample_inbox.updated_at is None


def test_inbox_update(sample_inbox):
    """Test updating an inbox's description and updated_at timestamp."""
    old_updated_at = sample_inbox.updated_at
    sample_inbox.update("Updated Description")

    assert sample_inbox.description == "Updated Description"
    assert sample_inbox.updated_at is not None
    assert sample_inbox.updated_at > sample_inbox.created_at
    if old_updated_at:
        assert sample_inbox.updated_at > old_updated_at


def test_inbox_delete(sample_inbox):
    """Test marking an inbox as deleted."""
    sample_inbox.delete()

    assert sample_inbox.status == InboxStatus.DELETED
    assert sample_inbox.updated_at is not None
    assert sample_inbox.updated_at > sample_inbox.created_at


def test_inbox_move(sample_inbox):
    """Test marking an inbox as moved."""
    sample_inbox.move()

    assert sample_inbox.status == InboxStatus.MOVED
    assert sample_inbox.updated_at is not None
    assert sample_inbox.updated_at > sample_inbox.created_at


def test_inbox_fields_are_mutable(sample_inbox):
    """Test that Inbox fields can be modified directly."""
    # Create new values
    new_id = uuid.uuid4()
    new_user_id = UserId(str(uuid.uuid4()))
    new_created_at = datetime.now(timezone.utc) - timedelta(days=1)
    
    # Modify the fields
    sample_inbox.id = new_id
    sample_inbox.user_id = new_user_id
    sample_inbox.created_at = new_created_at
    
    # Verify the changes
    assert sample_inbox.id == new_id
    assert sample_inbox.user_id == new_user_id
    assert sample_inbox.created_at == new_created_at
