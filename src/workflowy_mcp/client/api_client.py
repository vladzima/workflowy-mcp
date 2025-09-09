"""WorkFlowy API client implementation."""

import json
from typing import Any, Dict, List, Optional
import httpx
from pydantic import SecretStr

from ..models import (
    WorkFlowyNode,
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeListRequest,
    APIConfiguration,
    AuthenticationError,
    NodeNotFoundError,
    NetworkError,
    TimeoutError,
    RateLimitError,
)


class WorkFlowyClient:
    """Async client for WorkFlowy API operations."""
    
    def __init__(self, config: APIConfiguration):
        """Initialize the WorkFlowy API client."""
        self.config = config
        self.base_url = config.base_url
        self._client: Optional[httpx.AsyncClient] = None
    
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
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key or unauthorized access")
        
        if response.status_code == 404:
            raise NodeNotFoundError(
                node_id=response.request.url.path.split("/")[-1],
                message="Resource not found"
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
            return response.json()
        except json.JSONDecodeError:
            raise NetworkError("Invalid response format from API")
    
    async def create_node(self, request: NodeCreateRequest) -> WorkFlowyNode:
        """Create a new node in WorkFlowy."""
        try:
            response = await self.client.post(
                "/nodes",
                json=request.model_dump(exclude_none=True)
            )
            data = await self._handle_response(response)
            return WorkFlowyNode(**data)
        except httpx.TimeoutException:
            raise TimeoutError("create_node")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def update_node(self, node_id: str, request: NodeUpdateRequest) -> WorkFlowyNode:
        """Update an existing node."""
        try:
            response = await self.client.patch(
                f"/nodes/{node_id}",
                json=request.model_dump(exclude_none=True)
            )
            data = await self._handle_response(response)
            return WorkFlowyNode(**data)
        except httpx.TimeoutException:
            raise TimeoutError("update_node")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def get_node(self, node_id: str) -> WorkFlowyNode:
        """Retrieve a specific node by ID."""
        try:
            response = await self.client.get(f"/nodes/{node_id}")
            data = await self._handle_response(response)
            return WorkFlowyNode(**data)
        except httpx.TimeoutException:
            raise TimeoutError("get_node")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def list_nodes(self, request: NodeListRequest) -> tuple[List[WorkFlowyNode], int]:
        """List nodes with optional filtering."""
        try:
            params = request.model_dump(exclude_none=True)
            response = await self.client.get("/nodes", params=params)
            data = await self._handle_response(response)
            
            nodes = [WorkFlowyNode(**node_data) for node_data in data.get("nodes", [])]
            total = data.get("total", len(nodes))
            return nodes, total
        except httpx.TimeoutException:
            raise TimeoutError("list_nodes")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def delete_node(self, node_id: str) -> bool:
        """Delete a node and all its children."""
        try:
            response = await self.client.delete(f"/nodes/{node_id}")
            await self._handle_response(response)
            return True
        except httpx.TimeoutException:
            raise TimeoutError("delete_node")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def complete_node(self, node_id: str) -> WorkFlowyNode:
        """Mark a node as completed."""
        try:
            response = await self.client.post(f"/nodes/{node_id}/complete")
            data = await self._handle_response(response)
            return WorkFlowyNode(**data)
        except httpx.TimeoutException:
            raise TimeoutError("complete_node")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def uncomplete_node(self, node_id: str) -> WorkFlowyNode:
        """Mark a node as not completed."""
        try:
            response = await self.client.post(f"/nodes/{node_id}/uncomplete")
            data = await self._handle_response(response)
            return WorkFlowyNode(**data)
        except httpx.TimeoutException:
            raise TimeoutError("uncomplete_node")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def search_nodes(self, query: str, include_completed: bool = True) -> List[WorkFlowyNode]:
        """Search for nodes by text content."""
        try:
            params = {
                "q": query,
                "include_completed": include_completed
            }
            response = await self.client.get("/nodes/search", params=params)
            data = await self._handle_response(response)
            
            return [WorkFlowyNode(**node_data) for node_data in data.get("nodes", [])]
        except httpx.TimeoutException:
            raise TimeoutError("search_nodes")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")