"""Request and response models for WorkFlowy operations."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator

from .node import WorkFlowyNode


class NodeCreateRequest(BaseModel):
    """Request payload for creating a new node."""

    parentId: Optional[str] = Field(None, description="Parent node ID (null for root level)")
    nm: str = Field(..., description="Name/text content (required)")
    no: Optional[str] = Field(None, description="Note content (optional)")
    priority: Optional[int] = Field(None, ge=0, le=3, description="Priority level (optional)")

    @field_validator("nm")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Node name must be non-empty")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        """Ensure priority is within valid range."""
        if v is not None and (v < 0 or v > 3):
            raise ValueError("Priority must be between 0 and 3")
        return v


class NodeUpdateRequest(BaseModel):
    """Request payload for updating an existing node."""

    nm: Optional[str] = Field(None, description="New name/text content")
    no: Optional[str] = Field(None, description="New note content")
    priority: Optional[int] = Field(None, ge=0, le=3, description="New priority level")
    parentId: Optional[str] = Field(None, description="New parent (for moving nodes)")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        """Ensure priority is within valid range."""
        if v is not None and (v < 0 or v > 3):
            raise ValueError("Priority must be between 0 and 3")
        return v

    def has_updates(self) -> bool:
        """Check if at least one field is provided for update."""
        return any(getattr(self, field) is not None for field in self.model_fields)


class NodeListRequest(BaseModel):
    """Request parameters for listing/searching nodes."""

    parentId: Optional[str] = Field(None, description="Filter by parent node")
    completed: Optional[bool] = Field(None, description="Filter by completion status")
    query: Optional[str] = Field(None, description="Search query for text content")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(0, ge=0, description="Pagination offset")

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Ensure limit is within acceptable range."""
        if v < 1:
            raise ValueError("Limit must be at least 1")
        if v > 1000:
            raise ValueError("Limit cannot exceed 1000")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Ensure offset is non-negative."""
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v


class NodeResponse(BaseModel):
    """Response for single node operations."""

    node: WorkFlowyNode
    success: bool = True
    message: Optional[str] = None


class NodeListResponse(BaseModel):
    """Response for listing multiple nodes."""

    nodes: List[WorkFlowyNode]
    total: int
    success: bool = True
    hasMore: bool = False
    nextOffset: Optional[int] = None


class DeleteResponse(BaseModel):
    """Response for delete operations."""

    success: bool = True
    deleted: bool = True
    message: str = "Node deleted successfully"
    nodeId: Optional[str] = None


class SearchRequest(BaseModel):
    """Request for searching nodes."""

    query: str = Field(..., min_length=1, description="Search query string")
    includeCompleted: bool = Field(True, description="Include completed nodes in results")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Ensure query is not empty."""
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()


class SearchResponse(BaseModel):
    """Response for search operations."""

    nodes: List[WorkFlowyNode]
    total: int
    query: str
    success: bool = True
