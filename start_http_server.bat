@echo off
REM CAILculator MCP Server - HTTP Mode Launcher
REM For Gemini CLI and other HTTP-based MCP clients

echo.
echo ============================================================
echo   CAILculator MCP Server - HTTP Mode
echo ============================================================
echo.

REM Check if API key is set
if "%CAILCULATOR_API_KEY%"=="" (
    echo ERROR: CAILCULATOR_API_KEY environment variable not set
    echo.
    echo Set your API key with:
    echo   set CAILCULATOR_API_KEY=your_api_key_here
    echo.
    echo Get an API key at paul@chavezailabs.com
    echo.
    pause
    exit /b 1
)

echo Starting HTTP server on http://localhost:8080
echo.
echo Available endpoints:
echo   - GET  /mcp/manifest    (Tool definitions for Gemini CLI)
echo   - POST /message         (MCP JSON-RPC messages)
echo   - GET  /health          (Health check)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start server using venv Python
"%~dp0venv\Scripts\python.exe" -m cailculator_mcp.server --transport http --port 8080
