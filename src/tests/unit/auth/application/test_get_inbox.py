import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from src.auth.application.user_cases import GetInbox
from src.auth.domain.entities import Inbox, InboxStatus, UserId


@pytest.fixture
def mock_inbox_repository():
    return Mock()

def test_get_inbox_success(mock_inbox_repository):
    # Arrange
    user_id = UserId("123e4567-e89b-12d3-a456-426614174000")
    inbox_id = "test-inbox-123"
    
    expected_inbox = Inbox(
        id=inbox_id,
        user_id=user_id,
        description="Test Inbox",
        status=InboxStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )
    
    mock_inbox_repository.get_by_inbox_id.return_value = expected_inbox
    
    # Create the use case
    get_inbox = GetInbox(inboxes=mock_inbox_repository)
    
    # Act
    result = get_inbox.execute(inbox_id=inbox_id)
    
    # Assert
    assert result == expected_inbox
    mock_inbox_repository.get_by_inbox_id.assert_called_once_with(inbox_id)

def test_get_inbox_not_found(mock_inbox_repository):
    # Arrange
    inbox_id = "non-existent-inbox"
    mock_inbox_repository.get_by_inbox_id.return_value = None
    
    # Create the use case
    get_inbox = GetInbox(inboxes=mock_inbox_repository)
    
    # Act & Assert
    result = get_inbox.execute(inbox_id=inbox_id)
    assert result is None
    mock_inbox_repository.get_by_inbox_id.assert_called_once_with(inbox_id)
