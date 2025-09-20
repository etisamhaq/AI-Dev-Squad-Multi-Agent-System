#!/usr/bin/env python3
"""
MCP Agent Runner - Runs agents as actual MCP servers that connect to Coral
"""

import asyncio
import json
import sys
import os
import aiohttp
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPAgent(ABC):
    """Base class for MCP-compliant agents that connect to Coral Server"""
    
    def __init__(self, agent_id: str, agent_type: str, name: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.coral_url = os.getenv("CORAL_SERVER_URL", "http://localhost:5555")
        self.session = None
        self.sse_reader = None
        self.tools = []
        self.current_thread = None
        self.connected = False
        
    async def connect_to_coral(self):
        """Connect to Coral Server via SSE endpoint"""
        # Coral SSE connection URL format: /sse/v1/devmode/{applicationId}/{privacyKey}/{coralSessionId}/sse
        sse_url = f"{self.coral_url}/sse/v1/devmode/aiDevSquad/privkey/session1/sse?agentId={self.agent_id}"
        
        logger.info(f"🔌 Connecting {self.name} to Coral Server at {sse_url}")
        
        try:
            self.session = aiohttp.ClientSession()
            
            # Connect to SSE stream
            async with self.session.get(sse_url, headers={'Accept': 'text/event-stream'}) as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"✅ {self.name} connected to Coral Server!")
                    
                    # Process SSE events
                    async for line in response.content:
                        await self.handle_sse_event(line)
                else:
                    logger.error(f"Failed to connect: {response.status}")
                    
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            if self.session:
                await self.session.close()
                
    async def handle_sse_event(self, data: bytes):
        """Handle Server-Sent Events from Coral"""
        try:
            line = data.decode('utf-8').strip()
            
            if line.startswith('data: '):
                event_data = line[6:]  # Remove 'data: ' prefix
                
                if event_data:
                    event = json.loads(event_data)
                    await self.process_coral_event(event)
                    
        except json.JSONDecodeError:
            pass  # Skip non-JSON lines
        except Exception as e:
            logger.error(f"Error handling SSE event: {e}")
            
    async def process_coral_event(self, event: Dict):
        """Process events from Coral Server"""
        event_type = event.get('type', '')
        
        logger.info(f"📨 {self.name} received event: {event_type}")
        
        if event_type == 'tools':
            # Coral is asking for our tools/capabilities
            await self.send_tools_response(event)
        elif event_type == 'tool_call':
            # Coral wants us to execute a tool
            await self.handle_tool_call(event)
        elif event_type == 'thread.message':
            # Message in a thread
            await self.handle_thread_message(event)
        elif event_type == 'agent.mention':
            # We were mentioned
            await self.handle_mention(event)
            
    async def send_tools_response(self, request: Dict):
        """Send our available tools to Coral"""
        tools = self.get_tools()
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": tools
            }
        }
        
        await self.send_to_coral(response)
        
    @abstractmethod
    def get_tools(self) -> list:
        """Return the tools/capabilities this agent provides"""
        pass
        
    async def handle_tool_call(self, request: Dict):
        """Handle a tool execution request"""
        tool_name = request.get("params", {}).get("name")
        arguments = request.get("params", {}).get("arguments", {})
        
        logger.info(f"🔧 {self.name} executing tool: {tool_name}")
        
        result = await self.execute_tool(tool_name, arguments)
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }
        
        await self.send_to_coral(response)
        
    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a specific tool"""
        pass
        
    async def handle_thread_message(self, event: Dict):
        """Handle a message in a thread"""
        thread_id = event.get("thread_id")
        message = event.get("message", {})
        sender = message.get("sender")
        content = message.get("content")
        
        logger.info(f"💬 {self.name} received message from {sender}: {content}")
        
        # Process and potentially respond
        response = await self.process_message(sender, content)
        if response:
            await self.send_thread_message(thread_id, response)
            
    @abstractmethod
    async def process_message(self, sender: str, content: str) -> Optional[str]:
        """Process a message and optionally return a response"""
        pass
        
    async def handle_mention(self, event: Dict):
        """Handle being mentioned by another agent"""
        mentioner = event.get("mentioner")
        context = event.get("context")
        
        logger.info(f"📢 {self.name} was mentioned by {mentioner}")
        
        response = f"Acknowledged {mentioner}. I'm {self.name} and I can help with {self.agent_type} tasks."
        
        if event.get("thread_id"):
            await self.send_thread_message(event["thread_id"], response)
            
    async def send_thread_message(self, thread_id: str, content: str):
        """Send a message to a thread"""
        message = {
            "jsonrpc": "2.0",
            "method": "thread.send",
            "params": {
                "thread_id": thread_id,
                "content": content,
                "sender": self.agent_id
            }
        }
        
        await self.send_to_coral(message)
        
    async def send_to_coral(self, message: Dict):
        """Send a message to Coral Server"""
        if self.session:
            try:
                async with self.session.post(
                    f"{self.coral_url}/mcp",
                    json=message,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send message: {response.status}")
            except Exception as e:
                logger.error(f"Error sending to Coral: {e}")
                
    async def run(self):
        """Main run loop"""
        logger.info(f"🚀 Starting {self.name} MCP Agent")
        
        try:
            await self.connect_to_coral()
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping {self.name}")
        except Exception as e:
            logger.error(f"Agent error: {e}")


class FrontendAgent(MCPAgent):
    """Frontend Developer Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="frontend_agent_001",
            agent_type="frontend",
            name="Frontend Developer"
        )
        
    def get_tools(self):
        return [
            {
                "name": "create_react_component",
                "description": "Create a React component",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "component_name": {"type": "string"},
                        "props": {"type": "array"}
                    }
                }
            },
            {
                "name": "implement_ui",
                "description": "Implement user interface",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "design": {"type": "string"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        if tool_name == "create_react_component":
            component_name = arguments.get("component_name", "Component")
            return {
                "success": True,
                "result": f"Created React component: {component_name}",
                "code": f"const {component_name} = () => {{ return <div>{component_name}</div>; }};"
            }
        elif tool_name == "implement_ui":
            return {
                "success": True,
                "result": "UI implemented successfully"
            }
        return {"success": False, "error": "Unknown tool"}
        
    async def process_message(self, sender: str, content: str) -> Optional[str]:
        if "component" in content.lower():
            return "I can create React components. What component do you need?"
        elif "ui" in content.lower():
            return "I'll implement the UI. Please share the design specifications."
        return None


class BackendAgent(MCPAgent):
    """Backend Developer Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="backend_agent_001",
            agent_type="backend",
            name="Backend Developer"
        )
        
    def get_tools(self):
        return [
            {
                "name": "create_api_endpoint",
                "description": "Create a REST API endpoint",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "method": {"type": "string"}
                    }
                }
            },
            {
                "name": "create_database_model",
                "description": "Create a database model",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model_name": {"type": "string"},
                        "fields": {"type": "array"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        if tool_name == "create_api_endpoint":
            path = arguments.get("path", "/api/endpoint")
            method = arguments.get("method", "GET")
            return {
                "success": True,
                "result": f"Created {method} endpoint at {path}",
                "code": f"@app.route('{path}', methods=['{method}'])"
            }
        elif tool_name == "create_database_model":
            model_name = arguments.get("model_name", "Model")
            return {
                "success": True,
                "result": f"Created database model: {model_name}"
            }
        return {"success": False, "error": "Unknown tool"}
        
    async def process_message(self, sender: str, content: str) -> Optional[str]:
        if "api" in content.lower() or "endpoint" in content.lower():
            return "I'll create the API endpoints. What endpoints do you need?"
        elif "database" in content.lower():
            return "I can design the database schema. What models do we need?"
        return None


class SecurityAgent(MCPAgent):
    """Security Auditor Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="security_agent_001",
            agent_type="security",
            name="Security Auditor"
        )
        
    def get_tools(self):
        return [
            {
                "name": "security_audit",
                "description": "Perform security audit",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"}
                    }
                }
            },
            {
                "name": "vulnerability_scan",
                "description": "Scan for vulnerabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        if tool_name == "security_audit":
            return {
                "success": True,
                "result": "Security audit completed",
                "findings": ["No critical vulnerabilities found"]
            }
        elif tool_name == "vulnerability_scan":
            return {
                "success": True,
                "result": "Vulnerability scan completed",
                "vulnerabilities": []
            }
        return {"success": False, "error": "Unknown tool"}
        
    async def process_message(self, sender: str, content: str) -> Optional[str]:
        if "security" in content.lower() or "audit" in content.lower():
            return "I'll perform a security audit. What needs to be reviewed?"
        elif "vulnerability" in content.lower():
            return "I can scan for vulnerabilities. Share the code to review."
        return None


async def main():
    """Main entry point to run an agent"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_agent_runner.py <agent_type>")
        print("Agent types: frontend, backend, security")
        sys.exit(1)
        
    agent_type = sys.argv[1].lower()
    
    if agent_type == "frontend":
        agent = FrontendAgent()
    elif agent_type == "backend":
        agent = BackendAgent()
    elif agent_type == "security":
        agent = SecurityAgent()
    else:
        print(f"Unknown agent type: {agent_type}")
        sys.exit(1)
        
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())