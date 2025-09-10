"""Configuration models for WorkFlowy MCP server."""

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings


class APIConfiguration(BaseModel):
    """Server configuration for WorkFlowy API access."""

    api_key: SecretStr = Field(..., description="WorkFlowy API authentication key")
    base_url: str = Field("https://workflowy.com/api/v1", description="API base URL")
    timeout: int = Field(30, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, description="Maximum retry attempts")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Ensure API key is not empty."""
        if not v or not v.get_secret_value().strip():
            raise ValueError("API key must be non-empty")
        return v

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Ensure base URL is HTTPS."""
        if not v.startswith("https://"):
            raise ValueError("API base URL must use HTTPS")
        # Remove trailing slash for consistency
        return v.rstrip("/")

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Ensure timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Ensure max_retries is non-negative."""
        if v < 0:
            raise ValueError("Max retries must be non-negative")
        return v


class ServerConfig(BaseSettings):
    """Main server configuration using environment variables."""

    # WorkFlowy API settings
    workflowy_api_key: SecretStr = Field(
        ..., description="WorkFlowy API key", alias="WORKFLOWY_API_KEY"
    )
    workflowy_api_url: str = Field(
        "https://workflowy.com/api/v1",
        description="WorkFlowy API base URL",
        alias="WORKFLOWY_API_URL",
    )
    workflowy_timeout: int = Field(
        30, description="API request timeout in seconds", alias="WORKFLOWY_TIMEOUT"
    )
    workflowy_max_retries: int = Field(
        3, description="Maximum retry attempts", alias="WORKFLOWY_MAX_RETRIES"
    )

    # Server settings
    debug: bool = Field(False, description="Enable debug mode", alias="DEBUG")
    log_level: str = Field("INFO", description="Logging level", alias="LOG_LEVEL")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}

    def get_api_config(self) -> APIConfiguration:
        """Convert to APIConfiguration for the API client."""
        return APIConfiguration(
            api_key=self.workflowy_api_key,
            base_url=self.workflowy_api_url,
            timeout=self.workflowy_timeout,
            max_retries=self.workflowy_max_retries,
        )
