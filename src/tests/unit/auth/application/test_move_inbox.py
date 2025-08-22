import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from src.auth.application.user_cases import MoveInbox
from src.auth.domain.entities import Inbox, InboxStatus, UserId


@pytest.fixture
def mock_inbox_repository():
    return Mock()


def test_move_inbox_success(mock_inbox_repository):
    # Arrange
    user_id = UserId("123e4567-e89b-12d3-a456-426614174000")
    inbox_id = "test-inbox-123"

    # Create a mock inbox that will be returned by get_by_inbox_id
    mock_inbox = Mock()
    mock_inbox.id = inbox_id
    mock_inbox.user_id = user_id
    mock_inbox.status = InboxStatus.ACTIVE

    # Configure the mock repository
    mock_inbox_repository.get_by_inbox_id.return_value = mock_inbox

    # Create the use case
    move_inbox = MoveInbox(inboxes=mock_inbox_repository)

    # Act
    result = move_inbox.execute(inbox_id=inbox_id)

    # Assert
    mock_inbox_repository.get_by_inbox_id.assert_called_once_with(inbox_id)
    mock_inbox.move.assert_called_once()
    mock_inbox_repository.save.assert_called_once_with(mock_inbox)
    assert result == mock_inbox


def test_move_nonexistent_inbox(mock_inbox_repository):
    # Arrange
    inbox_id = "non-existent-inbox"
    mock_inbox_repository.get_by_inbox_id.return_value = None

    # Create the use case
    move_inbox = MoveInbox(inboxes=mock_inbox_repository)

    # Act & Assert
    with pytest.raises(ValueError, match=f"Inbox not found"):
        move_inbox.execute(inbox_id=inbox_id)
