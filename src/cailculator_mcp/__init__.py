"""
CAILculator MCP Server
High-dimensional data analysis for MCP clients
"""

__version__ = "0.1.0"
__author__ = "Paul Chavez"
__email__ = "paul@chavezailabs.com"

from .server import MCPServer, main
from .tools import TOOLS_DEFINITIONS, call_tool
from .patterns import PatternDetector, Pattern
from .hypercomplex import create_hypercomplex, Pathion, Sedenion

__all__ = [
    'MCPServer',
    'main',
    'TOOLS_DEFINITIONS',
    'call_tool',
    'PatternDetector',
    'Pattern',
    'create_hypercomplex',
    'Pathion',
    'Sedenion',
]
