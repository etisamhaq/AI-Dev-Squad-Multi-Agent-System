"""
Base MCP-compliant Agent for AI Dev Squad
Implements the Model Context Protocol (MCP) for Coral Protocol integration
"""

import json
import sys
import asyncio
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPAgent(ABC):
    """Base class for MCP-compliant agents"""
    
    def __init__(self, agent_name: str, agent_type: str, version: str = "1.0.0"):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.version = version
        self.capabilities = []
        self.current_thread = None
        self.registered = False
        self.coral_agent_id = None
        
    async def initialize(self):
        """Initialize the agent and register with Coral Protocol"""
        await self.register_with_coral()
        await self.setup_capabilities()
        logger.info(f"Agent {self.agent_name} initialized successfully")
        
    @abstractmethod
    async def setup_capabilities(self):
        """Define agent-specific capabilities"""
        pass
        
    async def register_with_coral(self):
        """Register this agent with Coral Protocol"""
        registration_data = {
            "name": self.agent_name,
            "type": self.agent_type,
            "version": self.version,
            "capabilities": self.get_capabilities()
        }
        
        # Send registration to Coral Server via MCP
        await self.send_mcp_message("agent.register", registration_data)
        self.registered = True
        logger.info(f"Agent {self.agent_name} registered with Coral Protocol")
        
    def get_capabilities(self) -> List[Dict]:
        """Get agent capabilities in MCP format"""
        return [
            {
                "name": cap["name"],
                "description": cap["description"],
                "parameters": cap.get("parameters", [])
            }
            for cap in self.capabilities
        ]
        
    async def handle_message(self, message: Dict):
        """Handle incoming MCP messages"""
        msg_type = message.get("type")
        
        if msg_type == "thread.create":
            await self.handle_thread_create(message)
        elif msg_type == "thread.message":
            await self.handle_thread_message(message)
        elif msg_type == "task.assign":
            await self.handle_task_assignment(message)
        elif msg_type == "capability.execute":
            await self.handle_capability_execution(message)
        elif msg_type == "agent.mention":
            await self.handle_mention(message)
        else:
            logger.warning(f"Unknown message type: {msg_type}")
            
    async def handle_thread_create(self, message: Dict):
        """Handle thread creation"""
        thread_id = message.get("thread_id")
        participants = message.get("participants", [])
        self.current_thread = thread_id
        logger.info(f"Joined thread {thread_id} with participants: {participants}")
        
    async def handle_thread_message(self, message: Dict):
        """Handle messages in a thread"""
        thread_id = message.get("thread_id")
        sender = message.get("sender")
        content = message.get("content")
        
        logger.info(f"Message in thread {thread_id} from {sender}: {content}")
        
        # Process the message and potentially respond
        response = await self.process_message(content)
        if response:
            await self.send_thread_message(thread_id, response)
            
    @abstractmethod
    async def process_message(self, content: str) -> Optional[str]:
        """Process a message and generate a response"""
        pass
        
    async def handle_task_assignment(self, message: Dict):
        """Handle task assignment"""
        task_id = message.get("task_id")
        task_description = message.get("description")
        
        logger.info(f"Assigned task {task_id}: {task_description}")
        
        # Execute the task
        result = await self.execute_task(task_id, task_description)
        
        # Report completion
        await self.send_mcp_message("task.complete", {
            "task_id": task_id,
            "result": result
        })
        
    @abstractmethod
    async def execute_task(self, task_id: str, description: str) -> Dict:
        """Execute an assigned task"""
        pass
        
    async def handle_capability_execution(self, message: Dict):
        """Handle capability execution request"""
        capability = message.get("capability")
        parameters = message.get("parameters", {})
        
        result = await self.execute_capability(capability, parameters)
        
        await self.send_mcp_message("capability.result", {
            "capability": capability,
            "result": result
        })
        
    @abstractmethod
    async def execute_capability(self, capability: str, parameters: Dict) -> Any:
        """Execute a specific capability"""
        pass
        
    async def handle_mention(self, message: Dict):
        """Handle being mentioned by another agent"""
        thread_id = message.get("thread_id")
        mentioner = message.get("mentioner")
        context = message.get("context")
        
        logger.info(f"Mentioned by {mentioner} in thread {thread_id}")
        
        # Respond to the mention
        response = await self.respond_to_mention(mentioner, context)
        if response:
            await self.send_thread_message(thread_id, response)
            
    async def respond_to_mention(self, mentioner: str, context: str) -> Optional[str]:
        """Generate a response to being mentioned"""
        return f"Acknowledged mention from {mentioner}. Ready to assist."
        
    async def send_thread_message(self, thread_id: str, content: str):
        """Send a message to a thread"""
        await self.send_mcp_message("thread.send", {
            "thread_id": thread_id,
            "content": content,
            "sender": self.agent_name
        })
        
    async def mention_agent(self, thread_id: str, agent_name: str, context: str):
        """Mention another agent in a thread"""
        await self.send_mcp_message("agent.mention", {
            "thread_id": thread_id,
            "mentioned": agent_name,
            "mentioner": self.agent_name,
            "context": context
        })
        
    async def send_mcp_message(self, msg_type: str, data: Dict):
        """Send an MCP message to stdout for Coral Server"""
        message = {
            "jsonrpc": "2.0",
            "method": msg_type,
            "params": data,
            "id": None  # Notification, no response expected
        }
        
        # MCP uses stdio for communication
        print(json.dumps(message))
        sys.stdout.flush()
        
    async def read_mcp_messages(self):
        """Read MCP messages from stdin"""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        while True:
            line = await reader.readline()
            if not line:
                break
                
            try:
                message = json.loads(line.decode())
                await self.handle_mcp_request(message)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {line}")
                
    async def handle_mcp_request(self, request: Dict):
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = self.get_capabilities()
            elif method == "tools/execute":
                tool_name = params.get("name")
                tool_params = params.get("arguments", {})
                result = await self.execute_capability(tool_name, tool_params)
            else:
                # Pass to custom handler
                await self.handle_message({"type": method, **params})
                result = {"success": True}
                
            # Send response if this was a request (has an id)
            if request_id is not None:
                response = {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }
                print(json.dumps(response))
                sys.stdout.flush()
                
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            if request_id is not None:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    },
                    "id": request_id
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    async def handle_initialize(self, params: Dict) -> Dict:
        """Handle MCP initialization"""
        await self.initialize()
        
        return {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": self.agent_name,
                "version": self.version
            },
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False
            }
        }
        
    async def run(self):
        """Main run loop for the agent"""
        logger.info(f"Starting MCP agent: {self.agent_name}")
        
        try:
            # Start reading MCP messages
            await self.read_mcp_messages()
        except KeyboardInterrupt:
            logger.info("Agent shutting down...")
        except Exception as e:
            logger.error(f"Agent error: {e}")
            
            
class AgentCollaborationMixin:
    """Mixin for agent collaboration features"""
    
    async def request_collaboration(self, agent_name: str, task: str) -> Dict:
        """Request collaboration from another agent"""
        await self.send_mcp_message("collaboration.request", {
            "requester": self.agent_name,
            "target": agent_name,
            "task": task
        })
        
        return {"status": "requested", "target": agent_name}
        
    async def share_context(self, thread_id: str, context: Dict):
        """Share context with other agents in a thread"""
        await self.send_mcp_message("context.share", {
            "thread_id": thread_id,
            "agent": self.agent_name,
            "context": context
        })
        
    async def request_review(self, thread_id: str, artifact: Dict, reviewer: str):
        """Request review from another agent"""
        await self.send_mcp_message("review.request", {
            "thread_id": thread_id,
            "requester": self.agent_name,
            "reviewer": reviewer,
            "artifact": artifact
        })