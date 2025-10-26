"""
CAILculator MCP Server
Main server implementation handling MCP protocol communication
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict

# Lazy imports to speed up server startup
# These will be imported only when needed
_auth_module = None
_config_module = None
_tools_module = None

def get_auth():
    global _auth_module
    if _auth_module is None:
        from .auth import validate_api_key as _validate
        _auth_module = type('obj', (object,), {'validate_api_key': _validate})
    return _auth_module

def get_config():
    global _config_module
    if _config_module is None:
        from .config import get_settings as _get_settings
        _config_module = type('obj', (object,), {'get_settings': _get_settings})
    return _config_module

def get_tools():
    global _tools_module
    if _tools_module is None:
        from .tools import TOOLS_DEFINITIONS as _tools_defs, call_tool as _call_tool
        _tools_module = type('obj', (object,), {'TOOLS_DEFINITIONS': _tools_defs, 'call_tool': _call_tool})
    return _tools_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Maximum response size (900KB to leave buffer before 1MB MCP limit)
MAX_RESPONSE_SIZE = 900_000


class MCPServer:
    """
    MCP (Model Context Protocol) Server for CAILculator
    
    Handles JSON-RPC 2.0 requests from MCP clients (like Claude Desktop)
    """
    
    def __init__(self):
        self._settings = None

    @property
    def settings(self):
        """Lazy load settings only when accessed."""
        if self._settings is None:
            self._settings = get_config().get_settings()
            logger.setLevel(self._settings.log_level)
        return self._settings
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming JSON-RPC 2.0 request.
        
        Args:
            request: JSON-RPC request dict with 'method', 'params', 'id'
            
        Returns:
            JSON-RPC response dict
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Received request: {method}")
        
        try:
            # Route to appropriate handler
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_list_tools(params)
            elif method == "tools/call":
                result = await self.handle_call_tool(params)
            elif method == "ping":
                result = {"status": "ok"}
            else:
                return self._error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )
            
            return {
                "jsonrpc": "2.0",
                "id": request_id if request_id is not None else 0,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return self._error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request from client."""
        logger.info("Initializing MCP server")
        
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "cailculator-mcp",
                "version": "0.2.0"
            },
            "capabilities": {
                "tools": {}
            }
        }
    
    async def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/list request - return available tools.

        Returns:
            Dict with 'tools' array
        """
        tools = get_tools()
        logger.info(f"Listing {len(tools.TOOLS_DEFINITIONS)} available tools")

        return {
            "tools": tools.TOOLS_DEFINITIONS
        }
    
    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request - execute a tool.
        
        Args:
            params: Must contain 'name' and 'arguments'
            
        Returns:
            Dict with 'content' array containing result
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name}")
        
        # Validate API key before executing tool
        api_key = self.settings.api_key
        
        if not api_key:
            logger.error("No API key provided")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": "No API key configured. Set CAILCULATOR_API_KEY environment variable."
                    })
                }],
                "isError": True
            }
        
        # Validate API key with auth server
        is_valid, error_message = await get_auth().validate_api_key(api_key)
        
        if not is_valid:
            logger.error(f"API key validation failed: {error_message}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": f"API key validation failed: {error_message}"
                    })
                }],
                "isError": True
            }
        
        # Execute the tool
        try:
            result = await get_tools().call_tool(tool_name, arguments)
            
            # Check response size to prevent 1MB limit errors
            result_json = json.dumps(result, indent=2)
            
            if len(result_json) > MAX_RESPONSE_SIZE:
                logger.warning(
                    f"Response too large ({len(result_json)} bytes), truncating for tool: {tool_name}"
                )
                
                # Create truncated response with summary
                truncated_result = {
                    "success": result.get("success", False),
                    "truncated": True,
                    "original_size_bytes": len(result_json),
                    "message": (
                        f"Response exceeded {MAX_RESPONSE_SIZE/1000:.0f}KB limit. "
                        "Key metrics and summary provided below."
                    ),
                    "tool": tool_name,
                    "summary": self._create_summary(result)
                }
                result_json = json.dumps(truncated_result, indent=2)
            
            return {
                "content": [{
                    "type": "text",
                    "text": result_json
                }]
            }
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": f"Tool execution failed: {str(e)}"
                    })
                }],
                "isError": True
            }
    
    def _create_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a compact summary of a large result.
        
        Args:
            result: Full result dict
            
        Returns:
            Compact summary dict with key metrics only
        """
        summary = {
            "success": result.get("success"),
            "operation": result.get("operation") or result.get("tool"),
        }
        
        # Include key metrics without large arrays
        if "dimension" in result:
            summary["dimension"] = result["dimension"]
        if "pattern_id" in result:
            summary["pattern_id"] = result["pattern_id"]
        if "interpretation" in result:
            summary["interpretation"] = result["interpretation"]
        if "metrics" in result:
            summary["metrics"] = result["metrics"]
        if "visualization_type" in result:
            summary["visualization_type"] = result["visualization_type"]
        if "static_path" in result:
            summary["static_path"] = result["static_path"]
        if "description" in result:
            summary["description"] = result["description"]
        
        # Add note about what was truncated
        if "result" in result:
            summary["result_truncated"] = "Coefficient array omitted (too large)"
        if "patterns" in result:
            patterns = result["patterns"]
            if isinstance(patterns, dict) and "patterns" in patterns:
                pattern_list = patterns["patterns"]
                summary["patterns_found"] = len(pattern_list)
                summary["pattern_types"] = list(set(p.get("type") for p in pattern_list[:5]))
        
        return summary
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id if request_id is not None else 0,
            "error": {
                "code": code,
                "message": message
            }
        }

    async def run(self):
        """
        Main server loop - read from stdin, write to stdout.
        
        MCP protocol uses stdio for communication.
        """
        logger.info("CAILculator MCP Server starting...")
        logger.info(f"Dev mode: {self.settings.enable_dev_mode}")
        logger.info(f"Auth endpoint: {self.settings.auth_endpoint}")
        
        while True:
            try:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    logger.info("EOF received, shutting down")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON-RPC request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
                
                # Handle request
                response = await self.handle_request(request)
                
                # Write response to stdout
                response_line = json.dumps(response)
                print(response_line, flush=True)
                
            except KeyboardInterrupt:
                logger.info("Interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                continue


def main():
    """Entry point for the MCP server."""
    server = MCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
