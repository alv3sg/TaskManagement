import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from src.auth.application.user_cases import GetInboxByUserId
from src.auth.domain.entities import Inbox, InboxStatus, UserId


@pytest.fixture
def mock_inbox_repository():
    return Mock()

def test_get_inbox_by_user_id_success(mock_inbox_repository):
    # Arrange
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    user_id_obj = UserId(user_id)
    
    sample_inboxes = [
        Inbox(
            id="inbox1",
            user_id=user_id_obj,
            description="Test Inbox 1",
            status=InboxStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        ),
        Inbox(
            id="inbox2",
            user_id=user_id_obj,
            description="Test Inbox 2",
            status=InboxStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        )
    ]
    
    mock_inbox_repository.get_by_user_id.return_value = sample_inboxes
    
    # Create the use case
    get_inbox = GetInboxByUserId(inboxes=mock_inbox_repository)
    
    # Act
    result = get_inbox.execute(user_id=user_id)
    
    # Assert
    assert len(result) == 2
    assert result[0].user_id == user_id_obj
    assert result[1].user_id == user_id_obj
    mock_inbox_repository.get_by_user_id.assert_called_once_with(user_id=user_id, limit=50, offset=0)

def test_get_inbox_by_user_id_with_pagination(mock_inbox_repository):
    # Arrange
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    user_id_obj = UserId(user_id)
    sample_inboxes = [
        Inbox(
            id="inbox1",
            user_id=user_id_obj,
            description="Test Inbox 1",
            status=InboxStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        )
    ]
    mock_inbox_repository.get_by_user_id.return_value = sample_inboxes
    
    get_inbox = GetInboxByUserId(inboxes=mock_inbox_repository)
    
    # Act
    result = get_inbox.execute(user_id=user_id, limit=10, offset=20)
    
    # Assert
    # The repository's get_by_user_id should be called with limit and offset parameters
    mock_inbox_repository.get_by_user_id.assert_called_once_with(
        user_id=user_id,
        limit=10,
        offset=20
    )
    assert len(result) == 1
    assert result[0].user_id == user_id_obj
