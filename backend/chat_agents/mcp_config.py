"""
MCP Configuration for Todo AI Chatbot
This module sets up the configuration for the Model Context Protocol server
"""

import os
from dotenv import load_dotenv

load_dotenv()

class MCPConfig:
    """Configuration class for MCP server settings"""

    def __init__(self):
        self.server_url = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
        self.port = int(os.getenv("MCP_SERVER_PORT", 3001))
        self.timeout = int(os.getenv("MCP_TIMEOUT", 30))
        self.max_retries = int(os.getenv("MCP_MAX_RETRIES", 3))

    def get_connection_params(self):
        """Get parameters for MCP server connection"""
        return {
            "url": self.server_url,
            "timeout": self.timeout,
            "retries": self.max_retries
        }

def create_mcp_config():
    """Factory function to create and return an MCPConfig instance"""
    return config


# Create a global config instance
config = MCPConfig()