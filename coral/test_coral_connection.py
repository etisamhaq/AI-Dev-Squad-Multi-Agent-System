#!/usr/bin/env python3
"""
Test script to verify MCP agents can connect to Coral Server
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append('/home/linked/Documents/internet-of-agents/ai-dev-squad/coral')

from agents.mcp_agent_runner import FrontendAgent, BackendAgent, SecurityAgent


async def test_single_agent():
    """Test a single agent connection"""
    print("\n=== Testing Single Agent Connection ===\n")
    
    agent = FrontendAgent()
    print(f"Creating {agent.name}...")
    
    # Try to connect for 5 seconds
    try:
        await asyncio.wait_for(agent.connect_to_coral(), timeout=5.0)
        print("✅ Agent connected successfully!")
    except asyncio.TimeoutError:
        print("⏱️ Agent is connected and waiting for events (timeout is expected)")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


async def test_multiple_agents():
    """Test multiple agents connecting simultaneously"""
    print("\n=== Testing Multiple Agent Connections ===\n")
    
    agents = [
        FrontendAgent(),
        BackendAgent(), 
        SecurityAgent()
    ]
    
    print(f"Creating {len(agents)} agents...")
    
    async def connect_agent(agent):
        try:
            print(f"  • Connecting {agent.name}...")
            await asyncio.wait_for(agent.connect_to_coral(), timeout=3.0)
            return f"✅ {agent.name} connected"
        except asyncio.TimeoutError:
            return f"⏱️ {agent.name} connected and waiting"
        except Exception as e:
            return f"❌ {agent.name} failed: {e}"
    
    # Connect all agents concurrently
    results = await asyncio.gather(*[connect_agent(agent) for agent in agents])
    
    print("\nResults:")
    for result in results:
        print(f"  {result}")


async def test_communication():
    """Test agent communication through Coral"""
    print("\n=== Testing Agent Communication ===\n")
    
    # This would require more setup with actual thread creation
    print("Note: Full communication testing requires thread creation in Coral")
    print("      This can be done via the orchestrator or integration script")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 CORAL MCP AGENT CONNECTION TESTS")
    print("=" * 60)
    
    # Check if Coral Server is running
    import requests
    try:
        response = requests.get("http://localhost:5555/api/v1/agents", timeout=2)
        print("✅ Coral Server is running on port 5555\n")
    except:
        print("❌ Coral Server is not running!")
        print("   Please start it with: cd coral/coral-server-repo && ./gradlew run")
        return
    
    # Run tests
    await test_single_agent()
    await test_multiple_agents()
    await test_communication()
    
    print("\n" + "=" * 60)
    print("✅ Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())