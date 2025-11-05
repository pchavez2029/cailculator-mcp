#!/bin/bash
# CAILculator MCP Server - HTTP Mode Launcher
# For Gemini CLI and other HTTP-based MCP clients

echo ""
echo "============================================================"
echo "  CAILculator MCP Server - HTTP Mode"
echo "============================================================"
echo ""

# Check if API key is set
if [ -z "$CAILCULATOR_API_KEY" ]; then
    echo "ERROR: CAILCULATOR_API_KEY environment variable not set"
    echo ""
    echo "Set your API key with:"
    echo "  export CAILCULATOR_API_KEY=your_api_key_here"
    echo ""
    echo "Get an API key at paul@chavezailabs.com"
    echo ""
    exit 1
fi

echo "Starting HTTP server on http://localhost:8080"
echo ""
echo "Available endpoints:"
echo "  - GET  /mcp/manifest    (Tool definitions for Gemini CLI)"
echo "  - POST /message         (MCP JSON-RPC messages)"
echo "  - GET  /health          (Health check)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start server using venv Python
"$SCRIPT_DIR/venv/bin/python" -m cailculator_mcp.server --transport http --port 8080
