import pytest
from unittest.mock import Mock, AsyncMock
from app.modules.user.repository import AuthRepository
from app.modules.user.model import User
import uuid


class TestAuthRepository:
    """Test cases for AuthRepository class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.auth_repository = AuthRepository(self.mock_session)
        
        # Create a sample User model instance
        self.sample_user = User(
            id=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            is_active=True,
            role="USER"
        )

    @pytest.mark.asyncio
    async def test_find_user_by_username_or_email_success(self):
        """Test finding user by username or email successfully."""
        # Arrange
        username = "testuser"
        
        # Mock the result object
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = self.sample_user
        
        self.mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await self.auth_repository.find_user_by_username_or_email(username)
        
        # Assert
        assert result == self.sample_user
        self.mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_user_by_username_or_email_not_found(self):
        """Test finding user by username or email when user doesn't exist."""
        # Arrange
        username = "nonexistent"
        
        # Mock the result object
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        
        self.mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await self.auth_repository.find_user_by_username_or_email(username)
        
        # Assert
        assert result is None
        self.mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test creating user successfully."""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "hashed_password"
        }
        
        self.mock_session.add = Mock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Act
        result = await self.auth_repository.create_user(user_data)
        
        # Assert
        assert isinstance(result, User)
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()

