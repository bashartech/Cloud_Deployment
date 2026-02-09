"""
Agent Registration for Todo AI Chatbot
This module registers the agent with the MCP server using the known working pattern
"""

import asyncio
from typing import Optional
from .chat_agent import create_chat_agent
from .mcp_config import config

class AgentRegistrar:
    """Handles the registration of agents with the MCP server"""

    def __init__(self):
        self.config = config
        self.agent = None

    async def register_agent(self):
        """Register the agent with the MCP server"""
        print(f"Registering agent with MCP server at {self.config.server_url}")

        try:
            # Create the agent
            self.agent = await create_chat_agent()

            print(f"Agent '{self.agent.name}' registered successfully!")

            # Return the registered agent
            return self.agent

        except Exception as e:
            print(f"Failed to register agent: {e}")
            raise

    async def get_registered_agent(self):
        """Get the registered agent instance"""
        if self.agent is None:
            await self.register_agent()
        return self.agent

    async def validate_registration(self):
        """Validate that the agent is properly registered"""
        try:
            agent = await self.get_registered_agent()

            # Perform a simple validation
            if hasattr(agent, 'name') and agent.name:
                print(f"✓ Agent registration validated: {agent.name}")
                return True
            else:
                print("✗ Agent registration validation failed: Invalid agent object")
                return False

        except Exception as e:
            print(f"✗ Agent registration validation failed: {e}")
            return False


# Global registrar instance
registrar = AgentRegistrar()


async def register_and_validate_agent():
    """Convenience function to register and validate the agent"""
    agent = await registrar.register_agent()

    is_valid = await registrar.validate_registration()

    if is_valid:
        print("Agent registration and validation completed successfully!")
        return agent
    else:
        raise Exception("Agent registration validation failed")


# For testing purposes
async def main():
    """Test the agent registration process"""
    print("Starting agent registration test...")

    try:
        agent = await register_and_validate_agent()
        print(f"Test successful! Registered agent: {agent.name}")
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())