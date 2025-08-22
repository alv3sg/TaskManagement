import uuid
from datetime import datetime, timezone
from unittest.mock import Mock, call, patch

import pytest

from src.auth.application.ports import UserRepository, InboxRepository
from src.auth.application.user_cases import CreateInbox
from src.auth.domain.entities import Inbox, User, UserId, Email, PasswordHash, UserStatus, InboxStatus


@pytest.fixture
def mock_user_repository():
    return Mock(spec=UserRepository)


@pytest.fixture
def mock_inbox_repository():
    return Mock(spec=InboxRepository)


@pytest.fixture
def sample_user():
    # Create a mock user with a valid password hash
    user = Mock(spec=User)
    user.id = UserId(uuid.uuid4())
    user.issue_inbox = Mock()
    
    # Create a sample inbox that will be returned by issue_inbox
    inbox = Inbox(
        id=uuid.uuid4(),
        user_id=user.id,
        description="Test Inbox",
        status=InboxStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )
    user.issue_inbox.return_value = inbox
    
    return user


def test_create_inbox_successfully(mock_user_repository, mock_inbox_repository, sample_user):
    # Arrange
    user_id = str(sample_user.id.value)
    description = "Test Inbox"
    
    # Configure the mock to return our sample user
    mock_user_repository.get_by_id.return_value = sample_user
    
    # Create the use case
    create_inbox = CreateInbox(users=mock_user_repository, inboxes=mock_inbox_repository)

    # Act
    result = create_inbox.execute(user_id=user_id, description=description)

    # Assert
    # Verify the user was retrieved
    mock_user_repository.get_by_id.assert_called_once()
    
    # Verify issue_inbox was called with the correct description
    sample_user.issue_inbox.assert_called_once_with(description)
    
    # Verify the inbox was added to the repository
    mock_inbox_repository.add.assert_called_once()
    
    # Get the inbox that was added
    added_inbox = mock_inbox_repository.add.call_args[0][0]
    
    # Verify the result is the same as the added inbox
    assert result == added_inbox


def test_create_inbox_calls_issue_inbox(mock_user_repository, mock_inbox_repository, sample_user):
    # Arrange
    user_id = str(sample_user.id.value)
    description = "Test Inbox"
    
    # Configure the mock to return our sample user
    mock_user_repository.get_by_id.return_value = sample_user
    
    # Create the use case
    create_inbox = CreateInbox(users=mock_user_repository, inboxes=mock_inbox_repository)

    # Act
    create_inbox.execute(user_id=user_id, description=description)

    # Assert that issue_inbox was called with the correct description
    sample_user.issue_inbox.assert_called_once_with(description)


def test_create_inbox_invalid_user_id(mock_user_repository, mock_inbox_repository, sample_user):
    # Arrange
    invalid_user_id = "not-a-valid-uuid"
    description = "Test Inbox"
    
    # Configure the mock to raise ValueError for invalid UUID
    def mock_get_by_id(user_id):
        # This simulates the behavior of UserId() raising ValueError for invalid UUID
        try:
            uuid.UUID(user_id.value)
            return sample_user
        except ValueError:
            raise ValueError(f"Invalid UUID format: {user_id}")
    
    mock_user_repository.get_by_id.side_effect = mock_get_by_id
    
    # Create the use case
    create_inbox = CreateInbox(users=mock_user_repository, inboxes=mock_inbox_repository)

    # Act & Assert - This should raise a ValueError when trying to create UserId
    with pytest.raises(ValueError) as exc_info:
        create_inbox.execute(user_id=invalid_user_id, description=description)
    
    # Verify the error message contains something about invalid UUID
    assert "invalid" in str(exc_info.value).lower()
