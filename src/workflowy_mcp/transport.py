"""STDIO transport handler for WorkFlowy MCP Server."""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a JSON-RPC message."""

    jsonrpc: str = "2.0"
    id: int | None = None
    method: str | None = None
    params: dict[str, Any] | None = None
    result: Any | None = None
    error: dict[str, Any] | None = None


class STDIOTransport:
    """
    STDIO transport implementation for MCP.

    Handles reading from stdin and writing to stdout in JSON-RPC format.
    """

    def __init__(self) -> None:
        """Initialize STDIO transport."""
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.running = False
        self.message_id = 0

    async def start(self) -> None:
        """Start the STDIO transport."""
        logger.info("Starting STDIO transport")
        self.running = True

        # Create async streams for stdin/stdout
        loop = asyncio.get_event_loop()
        self.reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(self.reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        w_transport, w_protocol = await loop.connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        self.writer = asyncio.StreamWriter(w_transport, w_protocol, self.reader, loop)

    async def stop(self) -> None:
        """Stop the STDIO transport."""
        logger.info("Stopping STDIO transport")
        self.running = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def read_message(self) -> Message | None:
        """
        Read a message from stdin.

        Returns:
            Parsed message or None if transport is stopped
        """
        if not self.running or not self.reader:
            return None

        try:
            # Read until we get a complete JSON object
            buffer = ""
            depth = 0
            in_string = False
            escape_next = False

            while self.running:
                char_bytes = await self.reader.read(1)
                if not char_bytes:
                    break

                char = char_bytes.decode("utf-8")
                buffer += char

                # Track JSON structure
                if not escape_next:
                    if char == '"' and not in_string:
                        in_string = True
                    elif char == '"' and in_string:
                        in_string = False
                    elif char == "\\" and in_string:
                        escape_next = True
                        continue
                    elif char == "{" and not in_string:
                        depth += 1
                    elif char == "}" and not in_string:
                        depth -= 1
                        if depth == 0 and buffer.strip():
                            # Complete JSON object
                            try:
                                data = json.loads(buffer)
                                return Message(**data)
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse message: {e}")
                                buffer = ""
                else:
                    escape_next = False

        except asyncio.CancelledError:
            logger.info("Read cancelled")
        except Exception as e:
            logger.error(f"Error reading message: {e}")

        return None

    async def write_message(self, message: Message) -> None:
        """
        Write a message to stdout.

        Args:
            message: Message to send
        """
        if not self.running or not self.writer:
            return

        try:
            # Convert message to dict
            data: dict[str, Any] = {
                "jsonrpc": message.jsonrpc,
            }

            if message.id is not None:
                data["id"] = message.id
            if message.method is not None:
                data["method"] = message.method
            if message.params is not None:
                data["params"] = message.params
            if message.result is not None:
                data["result"] = message.result
            if message.error is not None:
                data["error"] = message.error

            # Write as JSON with newline
            json_str = json.dumps(data) + "\n"
            self.writer.write(json_str.encode("utf-8"))
            await self.writer.drain()

        except Exception as e:
            logger.error(f"Error writing message: {e}")

    async def send_request(self, method: str, params: dict[str, Any] | None = None) -> int:
        """
        Send a request message.

        Args:
            method: Method name
            params: Optional parameters

        Returns:
            Message ID for tracking response
        """
        self.message_id += 1
        message = Message(id=self.message_id, method=method, params=params or {})
        await self.write_message(message)
        return self.message_id

    async def send_response(
        self, request_id: int, result: Any | None = None, error: dict[str, Any] | None = None
    ) -> None:
        """
        Send a response message.

        Args:
            request_id: ID of the request being responded to
            result: Result data (if successful)
            error: Error data (if failed)
        """
        message = Message(id=request_id, result=result, error=error)
        await self.write_message(message)

    async def send_notification(self, method: str, params: dict[str, Any] | None = None) -> None:
        """
        Send a notification message (no response expected).

        Args:
            method: Method name
            params: Optional parameters
        """
        message = Message(method=method, params=params or {})
        await self.write_message(message)


class TransportManager:
    """Manages the transport layer for the MCP server."""

    def __init__(self) -> None:
        """Initialize transport manager."""
        self.transport = STDIOTransport()
        self.handlers: dict[str, Any] = {}

    def register_handler(self, method: str, handler: Any) -> None:
        """
        Register a handler for a specific method.

        Args:
            method: Method name
            handler: Async function to handle the method
        """
        self.handlers[method] = handler

    async def handle_message(self, message: Message) -> None:
        """
        Handle an incoming message.

        Args:
            message: Message to process
        """
        if message.method and message.method in self.handlers:
            handler = self.handlers[message.method]
            try:
                result = await handler(message.params or {})
                if message.id is not None:
                    await self.transport.send_response(message.id, result=result)
            except Exception as e:
                logger.error(f"Error handling {message.method}: {e}")
                if message.id is not None:
                    await self.transport.send_response(
                        message.id, error={"code": -32603, "message": str(e)}
                    )
        elif message.id is not None:
            # Unknown method
            await self.transport.send_response(
                message.id, error={"code": -32601, "message": f"Method not found: {message.method}"}
            )

    async def run(self) -> None:
        """Run the transport manager."""
        await self.transport.start()

        try:
            while self.transport.running:
                message = await self.transport.read_message()
                if message:
                    await self.handle_message(message)
        finally:
            await self.transport.stop()


# Global transport manager instance
transport_manager = TransportManager()
