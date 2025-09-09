"""Unit tests for data models validation."""

import pytest
from typing import Any, Dict
import time

from workflowy_mcp.models.node import WorkFlowyNode
from workflowy_mcp.models.requests import (
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeListRequest,
    SearchRequest,
)
from workflowy_mcp.models.config import ServerConfig
from workflowy_mcp.models.errors import (
    WorkFlowyError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    NodeNotFoundError,
    NetworkError,
    TimeoutError,
    ErrorResponse,
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
        """Test that missing required fields raise errors."""
        with pytest.raises(ValueError):
            WorkFlowyNode(nm="Missing ID")  # Missing id

        with pytest.raises(ValueError):
            WorkFlowyNode(id="test-123")  # Missing created/modified


class TestRequestModels:
    """Test request model validation."""

    def test_create_request_valid(self):
        """Test valid create request."""
        request = NodeCreateRequest(
            nm="New Node", no="Node description", priority=2, parentId="parent-123"
        )
        assert request.nm == "New Node"
        assert request.no == "Node description"
        assert request.priority == 2
        assert request.parentId == "parent-123"

    def test_create_request_priority_validation(self):
        """Test priority validation in create request."""
        # Valid priorities
        for priority in [0, 1, 2, 3]:
            request = NodeCreateRequest(nm="Test", priority=priority)
            assert request.priority == priority

        # Invalid priorities
        with pytest.raises(ValueError):
            NodeCreateRequest(nm="Test", priority=-1)

        with pytest.raises(ValueError):
            NodeCreateRequest(nm="Test", priority=4)

    def test_update_request_partial(self):
        """Test update request with partial fields."""
        request = NodeUpdateRequest(nm="Updated Name")
        assert request.nm == "Updated Name"
        assert request.no is None
        assert request.priority is None
        assert request.parentId is None

    def test_list_request_pagination(self):
        """Test list request with pagination."""
        request = NodeListRequest(parentId="parent-123", completed=True, limit=50, offset=100)
        assert request.parentId == "parent-123"
        assert request.completed is True
        assert request.limit == 50
        assert request.offset == 100

    def test_search_request(self):
        """Test search request validation."""
        request = SearchRequest(query="project", includeCompleted=False)
        assert request.query == "project"
        assert request.includeCompleted is False

    def test_search_request_empty_query(self):
        """Test that empty query is rejected."""
        with pytest.raises(ValueError):
            SearchRequest(query="")


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
        assert config.workflowy_api_url == "https://api.workflowy.com"
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
        from pydantic import ValidationError as PydanticValidationError

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
            from workflowy_mcp.models.config import APIConfiguration
            from pydantic import SecretStr

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
