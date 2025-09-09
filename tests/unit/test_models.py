"""Unit tests for data models validation."""

import pytest
from typing import Any, Dict
import time

from workflowy_mcp.models.node import WorkFlowyNode
from workflowy_mcp.models.requests import (
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeListRequest,
    NodeSearchRequest,
)
from workflowy_mcp.models.config import ServerConfig
from workflowy_mcp.models.errors import (
    WorkFlowyError,
    APIError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
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
            modified=int(time.time())
        )
        assert node.id == "test-123"
        assert node.nm == "Test Node"
        assert node.no == "Test note"
        assert node.cp is False
        assert node.priority == 2

    def test_node_with_children(self):
        """Test node with children list."""
        child1 = WorkFlowyNode(
            id="child-1",
            nm="Child 1",
            created=int(time.time()),
            modified=int(time.time())
        )
        child2 = WorkFlowyNode(
            id="child-2",
            nm="Child 2",
            created=int(time.time()),
            modified=int(time.time())
        )
        
        parent = WorkFlowyNode(
            id="parent-1",
            nm="Parent",
            ch=[child1, child2],
            created=int(time.time()),
            modified=int(time.time())
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
            name="New Node",
            note="Node description",
            priority=2,
            parent_id="parent-123"
        )
        assert request.name == "New Node"
        assert request.note == "Node description"
        assert request.priority == 2
        assert request.parent_id == "parent-123"

    def test_create_request_priority_validation(self):
        """Test priority validation in create request."""
        # Valid priorities
        for priority in [0, 1, 2, 3]:
            request = NodeCreateRequest(name="Test", priority=priority)
            assert request.priority == priority
        
        # Invalid priorities
        with pytest.raises(ValueError):
            NodeCreateRequest(name="Test", priority=-1)
        
        with pytest.raises(ValueError):
            NodeCreateRequest(name="Test", priority=4)

    def test_update_request_partial(self):
        """Test update request with partial fields."""
        request = NodeUpdateRequest(
            node_id="test-123",
            name="Updated Name"
        )
        assert request.node_id == "test-123"
        assert request.name == "Updated Name"
        assert request.note is None
        assert request.priority is None

    def test_list_request_pagination(self):
        """Test list request with pagination."""
        request = NodeListRequest(
            parent_id="parent-123",
            include_completed=True,
            max_depth=3,
            limit=50,
            offset=100
        )
        assert request.parent_id == "parent-123"
        assert request.include_completed is True
        assert request.max_depth == 3
        assert request.limit == 50
        assert request.offset == 100

    def test_search_request(self):
        """Test search request validation."""
        request = NodeSearchRequest(
            query="project",
            include_completed=False
        )
        assert request.query == "project"
        assert request.include_completed is False

    def test_search_request_empty_query(self):
        """Test that empty query is rejected."""
        with pytest.raises(ValueError):
            NodeSearchRequest(query="")


class TestConfigModel:
    """Test configuration model validation."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ServerConfig()
        assert config.api_key == ""
        assert config.api_base_url == "https://beta.workflowy.com/api"
        assert config.request_timeout == 30
        assert config.max_retries == 3
        assert config.rate_limit_requests == 60
        assert config.rate_limit_window == 60
        assert config.log_level == "INFO"

    def test_custom_config(self):
        """Test custom configuration."""
        config = ServerConfig(
            api_key="test-key",
            api_base_url="https://custom.api.com",
            request_timeout=60,
            max_retries=5,
            rate_limit_requests=100,
            rate_limit_window=120,
            log_level="DEBUG"
        )
        assert config.api_key == "test-key"
        assert config.api_base_url == "https://custom.api.com"
        assert config.request_timeout == 60
        assert config.max_retries == 5
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 120
        assert config.log_level == "DEBUG"

    def test_config_validation(self):
        """Test configuration validation."""
        # Invalid timeout
        with pytest.raises(ValueError):
            ServerConfig(request_timeout=-1)
        
        # Invalid max retries
        with pytest.raises(ValueError):
            ServerConfig(max_retries=-1)
        
        # Invalid rate limit
        with pytest.raises(ValueError):
            ServerConfig(rate_limit_requests=0)


class TestErrorModels:
    """Test error model structures."""

    def test_api_error(self):
        """Test API error creation."""
        error = APIError(
            message="API request failed",
            status_code=500,
            response_body={"error": "Internal server error"}
        )
        assert error.message == "API request failed"
        assert error.status_code == 500
        assert error.response_body == {"error": "Internal server error"}

    def test_validation_error(self):
        """Test validation error with field details."""
        error = ValidationError(
            message="Validation failed",
            field="priority",
            value=5,
            constraint="Must be between 0 and 3"
        )
        assert error.message == "Validation failed"
        assert error.field == "priority"
        assert error.value == 5
        assert error.constraint == "Must be between 0 and 3"

    def test_rate_limit_error(self):
        """Test rate limit error with retry information."""
        error = RateLimitError(
            message="Rate limit exceeded",
            retry_after=60,
            limit=100,
            window=3600
        )
        assert error.message == "Rate limit exceeded"
        assert error.retry_after == 60
        assert error.limit == 100
        assert error.window == 3600

    def test_authentication_error(self):
        """Test authentication error."""
        error = AuthenticationError(
            message="Invalid API key",
            realm="WorkFlowy API"
        )
        assert error.message == "Invalid API key"
        assert error.realm == "WorkFlowy API"