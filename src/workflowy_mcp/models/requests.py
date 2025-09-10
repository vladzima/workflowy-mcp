"""Request and response models for WorkFlowy operations."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .node import WorkFlowyNode


class NodeCreateRequest(BaseModel):
    """Request payload for creating a new node."""

    parent_id: str | None = Field(None, description="Parent node ID ('None' for root level)")
    name: str = Field(..., description="Text content (required)")
    note: str | None = Field(None, description="Note content (optional)")
    layoutMode: Literal["bullets", "todo", "h1", "h2", "h3"] | None = Field(
        None, description="Display mode (bullets, todo, h1, h2, h3)"
    )
    position: Literal["top", "bottom"] | None = Field(
        "top", description="Position: 'top' or 'bottom' (default: 'top')"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Node name must be non-empty")
        return v

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, v: str | None) -> str | None:
        """Keep parent_id as-is - None means root level."""
        return v


class NodeUpdateRequest(BaseModel):
    """Request payload for updating an existing node."""

    name: str | None = Field(None, description="New text content")
    note: str | None = Field(None, description="New note content")
    layoutMode: Literal["bullets", "todo", "h1", "h2", "h3"] | None = Field(
        None, description="New display mode (bullets, todo, h1, h2, h3)"
    )

    def has_updates(self) -> bool:
        """Check if at least one field is provided for update."""
        return any(getattr(self, field) is not None for field in self.model_fields)


class NodeListRequest(BaseModel):
    """Request parameters for listing/searching nodes."""

    parentId: str | None = Field(None, description="Filter by parent node")
    completed: bool | None = Field(None, description="Filter by completion status")
    query: str | None = Field(None, description="Search query for text content")
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
    message: str | None = None


class NodeListResponse(BaseModel):
    """Response for listing multiple nodes."""

    nodes: list[WorkFlowyNode]
    total: int
    success: bool = True
    hasMore: bool = False
    nextOffset: int | None = None


class DeleteResponse(BaseModel):
    """Response for delete operations."""

    success: bool = True
    deleted: bool = True
    message: str = "Node deleted successfully"
    nodeId: str | None = None


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

    nodes: list[WorkFlowyNode]
    total: int
    query: str
    success: bool = True
