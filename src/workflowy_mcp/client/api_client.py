"""WorkFlowy API client implementation."""

import json
from typing import Any

import httpx

from ..models import (
    APIConfiguration,
    AuthenticationError,
    NetworkError,
    NodeCreateRequest,
    NodeListRequest,
    NodeNotFoundError,
    NodeUpdateRequest,
    RateLimitError,
    TimeoutError,
    WorkFlowyNode,
)


class WorkFlowyClient:
    """Async client for WorkFlowy API operations."""

    def __init__(self, config: APIConfiguration):
        """Initialize the WorkFlowy API client."""
        self.config = config
        self.base_url = config.base_url
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            headers = {
                "Authorization": f"Bearer {self.config.api_key.get_secret_value()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=httpx.Timeout(self.config.timeout),
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "WorkFlowyClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key or unauthorized access")

        if response.status_code == 404:
            raise NodeNotFoundError(
                node_id=response.request.url.path.split("/")[-1], message="Resource not found"
            )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(retry_after=int(retry_after) if retry_after else None)

        if response.status_code >= 500:
            raise NetworkError(f"Server error: {response.status_code}")

        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("error", "API request failed")
            except (json.JSONDecodeError, KeyError):
                message = f"API error: {response.status_code}"
            raise NetworkError(message)

        try:
            return response.json()  # type: ignore[no-any-return]
        except json.JSONDecodeError as err:
            raise NetworkError("Invalid response format from API") from err

    async def create_node(self, request: NodeCreateRequest) -> WorkFlowyNode:
        """Create a new node in WorkFlowy."""
        try:
            response = await self.client.post("/nodes/", json=request.model_dump(exclude_none=True))
            data = await self._handle_response(response)
            # Create endpoint returns just {"item_id": "..."}
            # We need to construct a minimal node response
            item_id = data.get("item_id")
            if not item_id:
                raise NetworkError(f"Invalid response from create endpoint: {data}")

            # Return a minimal node with just the ID and provided fields
            node_data = {
                "id": item_id,
                "name": request.name,
                "note": request.note,
            }
            if request.layoutMode:
                node_data["data"] = {"layoutMode": request.layoutMode}
            return WorkFlowyNode(**node_data)
        except httpx.TimeoutException as err:
            raise TimeoutError("create_node") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def update_node(self, node_id: str, request: NodeUpdateRequest) -> WorkFlowyNode:
        """Update an existing node."""
        try:
            response = await self.client.post(
                f"/nodes/{node_id}", json=request.model_dump(exclude_none=True)
            )
            data = await self._handle_response(response)
            # API returns the full node object
            return WorkFlowyNode(**data)
        except httpx.TimeoutException as err:
            raise TimeoutError("update_node") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def get_node(self, node_id: str) -> WorkFlowyNode:
        """Retrieve a specific node by ID."""
        try:
            response = await self.client.get(f"/nodes/{node_id}")
            data = await self._handle_response(response)
            # API returns the full node object
            return WorkFlowyNode(**data)
        except httpx.TimeoutException as err:
            raise TimeoutError("get_node") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def list_nodes(self, request: NodeListRequest) -> tuple[list[WorkFlowyNode], int]:
        """List nodes with optional filtering."""
        try:
            params = request.model_dump(exclude_none=True)
            response = await self.client.get("/nodes", params=params)
            response_data: list[Any] | dict[str, Any] = await self._handle_response(response)

            # Assuming API returns an array of nodes directly
            # (Need to verify actual response structure)
            nodes: list[WorkFlowyNode] = []
            if isinstance(response_data, dict):
                if "nodes" in response_data:
                    nodes = [WorkFlowyNode(**node_data) for node_data in response_data["nodes"]]
            elif isinstance(response_data, list):
                nodes = [WorkFlowyNode(**node_data) for node_data in response_data]

            total = len(nodes)  # API doesn't provide a total count
            return nodes, total
        except httpx.TimeoutException as err:
            raise TimeoutError("list_nodes") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def delete_node(self, node_id: str) -> bool:
        """Delete a node and all its children."""
        try:
            response = await self.client.delete(f"/nodes/{node_id}")
            # Delete endpoint returns just a message, not nested data
            await self._handle_response(response)
            return True
        except httpx.TimeoutException as err:
            raise TimeoutError("delete_node") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def complete_node(self, node_id: str) -> WorkFlowyNode:
        """Mark a node as completed."""
        try:
            response = await self.client.post(f"/nodes/{node_id}/complete")
            data = await self._handle_response(response)
            # API returns the full node object
            return WorkFlowyNode(**data)
        except httpx.TimeoutException as err:
            raise TimeoutError("complete_node") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def uncomplete_node(self, node_id: str) -> WorkFlowyNode:
        """Mark a node as not completed."""
        try:
            response = await self.client.post(f"/nodes/{node_id}/uncomplete")
            data = await self._handle_response(response)
            # API returns the full node object
            return WorkFlowyNode(**data)
        except httpx.TimeoutException as err:
            raise TimeoutError("uncomplete_node") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    async def search_nodes(self, query: str, include_completed: bool = True) -> list[WorkFlowyNode]:
        """Search for nodes by text content.

        Note: WorkFlowy API doesn't have a native search endpoint.
        This implementation fetches all nodes and filters locally.
        """
        try:
            # Fetch all nodes and filter locally
            params = {"include_completed": include_completed}
            response = await self.client.get("/nodes", params=params)
            data = await self._handle_response(response)

            all_nodes = [WorkFlowyNode(**node_data) for node_data in data.get("nodes", [])]

            # Filter nodes that contain the query in name or note
            query_lower = query.lower()
            filtered_nodes = [
                node
                for node in all_nodes
                if (node.nm and query_lower in node.nm.lower())
                or (node.no and query_lower in node.no.lower())
            ]

            return filtered_nodes
        except httpx.TimeoutException as err:
            raise TimeoutError("search_nodes") from err
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e
