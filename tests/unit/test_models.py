"""Unit tests for data models validation."""

import time

import pytest

from workflowy_mcp.models.config import ServerConfig
from workflowy_mcp.models.errors import (
    AuthenticationError,
    ErrorResponse,
    NetworkError,
    NodeNotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
    WorkFlowyError,
)
from workflowy_mcp.models.node import WorkFlowyNode
from workflowy_mcp.models.requests import (
    NodeCreateRequest,
    NodeListRequest,
    NodeUpdateRequest,
)


class TestNodeModel:
    """Test WorkFlowyNode model validation."""

    def test_valid_node_creation(self):
        """Test creating a valid node."""
        node = WorkFlowyNode(
            id="test-123",
            nm="Test Node",
            no="Test note",
            cp=False,
            priority=2,
            created=int(time.time()),
            modified=int(time.time()),
        )
        assert node.id == "test-123"
        assert node.nm == "Test Node"
        assert node.no == "Test note"
        assert node.cp is False
        assert node.priority == 2

    def test_node_with_children(self):
        """Test node with children list."""
        child1 = WorkFlowyNode(
            id="child-1", nm="Child 1", created=int(time.time()), modified=int(time.time())
        )
        child2 = WorkFlowyNode(
            id="child-2", nm="Child 2", created=int(time.time()), modified=int(time.time())
        )

        parent = WorkFlowyNode(
            id="parent-1",
            nm="Parent",
            ch=[child1, child2],
            created=int(time.time()),
            modified=int(time.time()),
        )

        assert len(parent.ch) == 2
        assert parent.ch[0].id == "child-1"
        assert parent.ch[1].id == "child-2"

    def test_node_missing_required_fields(self):
        """Test that only ID is required."""
        # ID is the only required field now
        with pytest.raises(ValueError):
            WorkFlowyNode(name="Missing ID")  # Missing id

        # This should work - ID is provided
        node = WorkFlowyNode(id="test-123")
        assert node.id == "test-123"


class TestRequestModels:
    """Test request model validation."""

    def test_create_request_valid(self):
        """Test valid create request."""
        request = NodeCreateRequest(
            name="New Node", note="Node description", parent_id="parent-123"
        )
        assert request.name == "New Node"
        assert request.note == "Node description"
        assert request.parent_id == "parent-123"

    def test_create_request_priority_validation(self):
        """Test priority validation in create request."""
        # Priority is no longer in the model
        request = NodeCreateRequest(name="Test")
        assert request.name == "Test"

    def test_update_request_partial(self):
        """Test update request with partial fields."""
        request = NodeUpdateRequest(name="Updated Name")
        assert request.name == "Updated Name"
        assert request.note is None
        assert request.layoutMode is None

    def test_list_request_with_parent(self):
        """Test list request with parent ID."""
        request = NodeListRequest(parentId="parent-123")
        assert request.parentId == "parent-123"


class TestConfigModel:
    """Test configuration model validation."""

    def test_default_config(self):
        """Test default configuration values."""
        # ServerConfig requires api_key, so we'll test with a provided key
        import os

        # Save and clear any existing env vars
        saved_env = {}
        for key in [
            "WORKFLOWY_API_KEY",
            "WORKFLOWY_API_URL",
            "WORKFLOWY_TIMEOUT",
            "WORKFLOWY_MAX_RETRIES",
            "DEBUG",
            "LOG_LEVEL",
        ]:
            if key in os.environ:
                saved_env[key] = os.environ[key]
                del os.environ[key]

        os.environ["WORKFLOWY_API_KEY"] = "test-key-123"
        config = ServerConfig()
        assert config.workflowy_api_key.get_secret_value() == "test-key-123"
        assert config.workflowy_api_url == "https://workflowy.com/api/v1"
        assert config.workflowy_timeout == 30
        assert config.workflowy_max_retries == 3
        assert config.debug is False
        assert config.log_level == "INFO"

        # Clean up and restore
        del os.environ["WORKFLOWY_API_KEY"]
        for key, value in saved_env.items():
            os.environ[key] = value

    def test_custom_config(self):
        """Test custom configuration."""
        import os

        # Save and clear any existing env vars
        saved_env = {}
        for key in [
            "WORKFLOWY_API_KEY",
            "WORKFLOWY_API_URL",
            "WORKFLOWY_TIMEOUT",
            "WORKFLOWY_MAX_RETRIES",
            "DEBUG",
            "LOG_LEVEL",
        ]:
            if key in os.environ:
                saved_env[key] = os.environ[key]
                del os.environ[key]

        # Set custom env values
        os.environ["WORKFLOWY_API_KEY"] = "test-key"
        os.environ["WORKFLOWY_API_URL"] = "https://custom.api.com"
        os.environ["WORKFLOWY_TIMEOUT"] = "60"
        os.environ["WORKFLOWY_MAX_RETRIES"] = "5"
        os.environ["DEBUG"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"

        config = ServerConfig()
        assert config.workflowy_api_key.get_secret_value() == "test-key"
        assert config.workflowy_api_url == "https://custom.api.com"
        assert config.workflowy_timeout == 60
        assert config.workflowy_max_retries == 5
        assert config.debug is True
        assert config.log_level == "DEBUG"

        # Clean up
        for key in [
            "WORKFLOWY_API_KEY",
            "WORKFLOWY_API_URL",
            "WORKFLOWY_TIMEOUT",
            "WORKFLOWY_MAX_RETRIES",
            "DEBUG",
            "LOG_LEVEL",
        ]:
            if key in os.environ:
                del os.environ[key]
        # Restore original values
        for key, value in saved_env.items():
            os.environ[key] = value

    def test_config_validation(self):
        """Test configuration validation when converting to APIConfiguration."""
        import os

        # Save and clear any existing env vars
        saved_env = {}
        for key in [
            "WORKFLOWY_API_KEY",
            "WORKFLOWY_API_URL",
            "WORKFLOWY_TIMEOUT",
            "WORKFLOWY_MAX_RETRIES",
        ]:
            if key in os.environ:
                saved_env[key] = os.environ[key]
                del os.environ[key]

        try:
            # Test APIConfiguration validation directly
            from pydantic import SecretStr

            from workflowy_mcp.models.config import APIConfiguration

            # Invalid timeout
            with pytest.raises(ValueError):
                APIConfiguration(api_key=SecretStr("test-key"), timeout=-1)

            # Invalid max retries
            with pytest.raises(ValueError):
                APIConfiguration(api_key=SecretStr("test-key"), max_retries=-1)

            # Empty API key
            with pytest.raises(ValueError):
                APIConfiguration(api_key=SecretStr(""))

            # Non-HTTPS URL
            with pytest.raises(ValueError):
                APIConfiguration(api_key=SecretStr("test-key"), base_url="http://api.workflowy.com")
        finally:
            # Restore original values
            for key, value in saved_env.items():
                os.environ[key] = value


class TestErrorModels:
    """Test error model structures."""

    def test_workflowy_error(self):
        """Test base WorkFlowy error creation."""
        error = WorkFlowyError(
            message="API request failed",
            code="API_ERROR",
            details={"error": "Internal server error"},
        )
        assert error.message == "API request failed"
        assert error.code == "API_ERROR"
        assert error.details == {"error": "Internal server error"}

    def test_validation_error(self):
        """Test validation error with field details."""
        error = ValidationError(
            message="Validation failed",
            field="priority",
        )
        assert error.message == "Validation failed"
        assert error.code == "VALIDATION_ERROR"
        assert error.details == {"field": "priority"}

    def test_rate_limit_error(self):
        """Test rate limit error with retry information."""
        error = RateLimitError(retry_after=60)
        assert error.message == "Rate limit exceeded. Retry after 60 seconds"
        assert error.code == "RATE_LIMIT_ERROR"
        assert error.details == {"retry_after": 60}

    def test_authentication_error(self):
        """Test authentication error."""
        error = AuthenticationError(message="Invalid API key", details={"realm": "WorkFlowy API"})
        assert error.message == "Invalid API key"
        assert error.code == "AUTH_ERROR"
        assert error.details == {"realm": "WorkFlowy API"}

    def test_node_not_found_error(self):
        """Test node not found error."""
        error = NodeNotFoundError(node_id="test-123")
        assert error.message == "Node with ID 'test-123' not found"
        assert error.code == "NODE_NOT_FOUND"
        assert error.details == {"node_id": "test-123"}

    def test_network_error(self):
        """Test network error."""
        error = NetworkError(message="Connection failed")
        assert error.message == "Connection failed"
        assert error.code == "NETWORK_ERROR"

    def test_timeout_error(self):
        """Test timeout error."""
        error = TimeoutError(operation="get_node")
        assert error.message == "Operation 'get_node' timed out"
        assert error.code == "TIMEOUT_ERROR"
        assert error.details == {"operation": "get_node"}

    def test_error_response(self):
        """Test error response model."""
        response = ErrorResponse(
            error="Something went wrong",
            code="GENERIC_ERROR",
            details={"trace_id": "abc123"},
        )
        assert response.error == "Something went wrong"
        assert response.code == "GENERIC_ERROR"
        assert response.details == {"trace_id": "abc123"}
        assert response.success is False
