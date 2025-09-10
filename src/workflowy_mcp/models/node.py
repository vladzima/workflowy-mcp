"""WorkFlowy node data model."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class WorkFlowyNode(BaseModel):
    """Represents a single node in the WorkFlowy outline hierarchy."""

    # API fields (what the API actually returns)
    id: str = Field(..., description="Unique identifier for the node")
    name: str | None = Field(None, alias="nm", description="Text content of the node")
    note: str | None = Field(None, alias="no", description="Note content attached to the node")
    priority: int | None = Field(None, description="Sort order")
    layoutMode: str | None = Field(None, description="Display mode (bullets, todo, h1, etc.)")
    createdAt: int | None = Field(
        None, alias="created", description="Creation timestamp (Unix timestamp)"
    )
    modifiedAt: int | None = Field(
        None, alias="modified", description="Last modification timestamp"
    )
    completedAt: int | None = Field(
        None, description="Completion timestamp (null if not completed)"
    )

    # Nested structure fields
    children: list["WorkFlowyNode"] | None = Field(None, alias="ch", description="Child nodes")
    parent_id: str | None = Field(None, alias="parentId", description="Parent node ID")

    # Handle 'cp' field for backward compatibility - we'll compute from completedAt
    completed_flag: bool | None = Field(
        None, alias="cp", description="Completion status (for tests)"
    )

    # Backward compatibility aliases for tests
    @property
    def nm(self) -> str | None:
        """Backward compatibility for name field."""
        return self.name

    @property
    def no(self) -> str | None:
        """Backward compatibility for note field."""
        return self.note

    @property
    def cp(self) -> bool:
        """Backward compatibility for completed status."""
        # Use completed_flag if it was set (from tests), otherwise check completedAt
        if self.completed_flag is not None:
            return self.completed_flag
        return self.completedAt is not None

    @property
    def ch(self) -> list["WorkFlowyNode"] | None:
        """Backward compatibility for children field."""
        return self.children

    @property
    def created(self) -> int:
        """Backward compatibility for created timestamp."""
        return self.createdAt or 0

    @property
    def modified(self) -> int:
        """Backward compatibility for modified timestamp."""
        return self.modifiedAt or 0

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is non-empty."""
        if not v or not v.strip():
            raise ValueError("Node ID must be non-empty")
        return v

    @field_validator("createdAt", "modifiedAt", "completedAt")
    @classmethod
    def validate_timestamp(cls, v: int | None) -> int | None:
        """Ensure timestamps are positive."""
        if v is not None and v <= 0:
            raise ValueError("Timestamp must be positive")
        return v

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Custom serialization to include backward compatibility fields."""
        data: dict[str, Any] = super().model_dump(**kwargs)

        # Add backward compatibility fields for tests
        data["nm"] = self.name
        data["no"] = self.note
        data["cp"] = self.cp
        data["ch"] = self.children
        data["created"] = self.createdAt or 0
        data["modified"] = self.modifiedAt or 0

        return data

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True  # Allow both field names and aliases
        json_schema_extra = {
            "example": {
                "id": "node-123",
                "name": "Example Node",
                "note": "This is a note",
                "priority": 1,
                "layoutMode": "bullets",
                "createdAt": 1704067200,
                "modifiedAt": 1704067200,
                "completedAt": None,
                "children": [],
            }
        }


# Enable forward references for recursive model
WorkFlowyNode.model_rebuild()
