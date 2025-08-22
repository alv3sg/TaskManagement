import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from src.auth.application.user_cases import ListInboxes
from src.auth.domain.entities import Inbox, InboxStatus, UserId


@pytest.fixture
def mock_inbox_repository():
    return Mock()

def test_list_inboxes_success(mock_inbox_repository):
    # Arrange
    user_id = UserId("123e4567-e89b-12d3-a456-426614174000")
    sample_inboxes = [
        Inbox(
            id="inbox1",
            user_id=user_id,
            description="Test Inbox 1",
            status=InboxStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        ),
        Inbox(
            id="inbox2",
            user_id=user_id,
            description="Test Inbox 2",
            status=InboxStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        )
    ]
    
    # Configure the mock to return our sample inboxes
    mock_inbox_repository.list.return_value = sample_inboxes
    
    # Create the use case
    list_inboxes = ListInboxes(inboxes=mock_inbox_repository)
    
    # Act
    result = list_inboxes.execute()
    
    # Assert
    assert len(result) == 2
    assert result[0].id == "inbox1"
    assert result[1].id == "inbox2"
    # The list method is called with default values
    mock_inbox_repository.list.assert_called_once()

def test_list_inboxes_with_pagination(mock_inbox_repository):
    # Arrange
    user_id = UserId("123e4567-e89b-12d3-a456-426614174000")
    sample_inboxes = [
        Inbox(
            id="inbox1",
            user_id=user_id,
            description="Test Inbox 1",
            status=InboxStatus.ACTIVE,
            created_at=datetime.now(timezone.utc)
        )
    ]
    mock_inbox_repository.list.return_value = sample_inboxes
    
    list_inboxes = ListInboxes(inboxes=mock_inbox_repository)
    
    # Act
    result = list_inboxes.execute(limit=10, offset=20)
    
    # Assert
    # The list method is called with the provided limit and offset
    mock_inbox_repository.list.assert_called_once_with(limit=10, offset=20)
    assert len(result) == 1
    assert result[0].id == "inbox1"
