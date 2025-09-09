"""WorkFlowy node data model."""

from pydantic import BaseModel, Field, field_validator


class WorkFlowyNode(BaseModel):
    """Represents a single node in the WorkFlowy outline hierarchy."""

    id: str = Field(..., description="Unique identifier for the node")
    nm: str | None = Field(None, description="Name/text content of the node")
    no: str | None = Field(None, description="Note content attached to the node")
    cp: bool = Field(False, description="Completion status (true if completed)")
    ch: list["WorkFlowyNode"] | None = Field(None, description="Child nodes")
    created: int = Field(..., description="Creation timestamp (Unix timestamp)")
    modified: int = Field(..., description="Last modification timestamp")
    priority: int | None = Field(None, ge=0, le=3, description="Priority level (0-3)")
    layout_mode: str | None = Field(None, description="Display layout mode")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is non-empty."""
        if not v or not v.strip():
            raise ValueError("Node ID must be non-empty")
        return v

    @field_validator("created", "modified")
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Ensure timestamps are positive."""
        if v <= 0:
            raise ValueError("Timestamp must be positive")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int | None) -> int | None:
        """Ensure priority is within valid range."""
        if v is not None and (v < 0 or v > 3):
            raise ValueError("Priority must be between 0 and 3")
        return v

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "node-123",
                "nm": "Example Node",
                "no": "This is a note",
                "cp": False,
                "created": 1704067200,
                "modified": 1704067200,
                "priority": 1,
                "ch": [],
            }
        }


# Enable forward references for recursive model
WorkFlowyNode.model_rebuild()
