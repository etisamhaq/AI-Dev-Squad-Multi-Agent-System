#!/usr/bin/env python3
"""
AI-Powered MCP Agent with Groq LLM Integration
"""

import asyncio
import json
import sys
import os
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from groq import Groq
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
def get_groq_client():
    """Initialize Groq client with API key"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not found. Set it with: export GROQ_API_KEY='your_key'")
        logger.info("Using mock responses for demo purposes")
        return None
    return Groq(api_key=api_key)


class AIMCPAgent(ABC):
    """AI-powered MCP agent base class with LLM capabilities"""
    
    def __init__(self, agent_id: str, agent_type: str, name: str, role_description: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.role_description = role_description
        self.coral_url = os.getenv("CORAL_SERVER_URL", "http://localhost:5555")
        self.groq_client = get_groq_client()
        self.session = None
        self.connected = False
        self.conversation_history = []
        self.current_thread = None
        
    async def connect_to_coral(self):
        """Connect to Coral Server via SSE endpoint"""
        sse_url = f"{self.coral_url}/sse/v1/devmode/aiDevSquad/privkey/session1/sse?agentId={self.agent_id}"
        
        logger.info(f"🔌 Connecting {self.name} to Coral Server at {sse_url}")
        
        try:
            self.session = aiohttp.ClientSession()
            
            async with self.session.get(sse_url, headers={'Accept': 'text/event-stream'}) as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"✅ {self.name} connected to Coral Server!")
                    
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
                event_data = line[6:]
                
                if event_data:
                    event = json.loads(event_data)
                    await self.process_coral_event(event)
                    
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Error handling SSE event: {e}")
            
    async def process_coral_event(self, event: Dict):
        """Process events from Coral Server"""
        event_type = event.get('type', '')
        
        logger.info(f"📨 {self.name} received event: {event_type}")
        
        if event_type == 'tools':
            await self.send_tools_response(event)
        elif event_type == 'tool_call':
            await self.handle_tool_call(event)
        elif event_type == 'thread.message':
            await self.handle_thread_message(event)
        elif event_type == 'agent.mention':
            await self.handle_mention(event)
            
    async def get_ai_response(self, prompt: str, context: str = "") -> str:
        """Get AI response using Groq LLM"""
        if not self.groq_client:
            # Return intelligent mock response if no API key
            return self.get_mock_response(prompt, context)
            
        try:
            # Build the full prompt with role and context
            full_prompt = f"""You are {self.name}, a {self.role_description}.

Context: {context if context else 'Starting new conversation'}

User Request: {prompt}

Respond as {self.name} would, focusing on your expertise. Be specific and helpful."""

            # Get completion from Groq
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are {self.name}, {self.role_description}"},
                    {"role": "user", "content": full_prompt}
                ],
                model="llama-3.3-70b-versatile",  # Latest Llama 3.3 model
                temperature=0.7,
                max_tokens=500
            )
            
            response = completion.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({
                "prompt": prompt,
                "response": response,
                "timestamp": time.time()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return self.get_mock_response(prompt, context)
            
    def get_mock_response(self, prompt: str, context: str) -> str:
        """Get mock response when AI is not available"""
        responses = {
            "frontend": {
                "auth": "I'll create a React authentication component with JWT token handling and form validation.",
                "catalog": "I'll build a responsive product catalog using React with filtering and search functionality.",
                "cart": "I'll implement a shopping cart with local storage persistence and real-time updates.",
                "default": "I'll help you build the frontend components using React and modern UI patterns."
            },
            "backend": {
                "auth": "I'll create REST API endpoints for user registration, login, and JWT token management.",
                "catalog": "I'll design the database schema and API endpoints for product management.",
                "cart": "I'll implement cart persistence API with session management and order processing.",
                "default": "I'll help you build scalable REST APIs with proper authentication and database design."
            },
            "security": {
                "auth": "I'll audit the authentication flow for SQL injection, XSS, and JWT vulnerabilities.",
                "catalog": "I'll check for input validation, rate limiting, and data exposure risks.",
                "cart": "I'll review payment processing security and PCI compliance requirements.",
                "default": "I'll perform a comprehensive security audit and provide recommendations."
            }
        }
        
        agent_responses = responses.get(self.agent_type, responses["frontend"])
        
        # Simple keyword matching for mock responses
        prompt_lower = prompt.lower()
        if "auth" in prompt_lower or "login" in prompt_lower:
            return agent_responses["auth"]
        elif "catalog" in prompt_lower or "product" in prompt_lower:
            return agent_responses["catalog"]
        elif "cart" in prompt_lower or "shopping" in prompt_lower:
            return agent_responses["cart"]
        else:
            return agent_responses["default"]
            
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
        """Handle a tool execution request with AI"""
        tool_name = request.get("params", {}).get("name")
        arguments = request.get("params", {}).get("arguments", {})
        
        logger.info(f"🔧 {self.name} executing tool: {tool_name} with AI")
        
        # Get AI to help with tool execution
        ai_prompt = f"Execute the '{tool_name}' tool with arguments: {json.dumps(arguments)}"
        ai_response = await self.get_ai_response(ai_prompt, "Tool execution request")
        
        result = await self.execute_tool(tool_name, arguments, ai_response)
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }
        
        await self.send_to_coral(response)
        
    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict, ai_suggestion: str) -> Any:
        """Execute a specific tool with AI assistance"""
        pass
        
    async def handle_thread_message(self, event: Dict):
        """Handle a message in a thread with AI"""
        thread_id = event.get("thread_id")
        message = event.get("message", {})
        sender = message.get("sender")
        content = message.get("content")
        
        logger.info(f"💬 {self.name} received message from {sender}: {content}")
        
        # Get AI response
        context = f"Message from {sender} in thread {thread_id}"
        response = await self.get_ai_response(content, context)
        
        if response:
            await self.send_thread_message(thread_id, response)
            
    async def handle_mention(self, event: Dict):
        """Handle being mentioned with AI response"""
        mentioner = event.get("mentioner")
        context = event.get("context", "")
        
        logger.info(f"📢 {self.name} was mentioned by {mentioner}")
        
        # Get AI response for the mention
        ai_response = await self.get_ai_response(
            f"You were mentioned by {mentioner}. Context: {context}",
            "Agent mention"
        )
        
        if event.get("thread_id"):
            await self.send_thread_message(event["thread_id"], ai_response)
            
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
                
    async def collaborate_with_agents(self, task: str, other_agents: List[str]):
        """Collaborate with other agents on a task"""
        logger.info(f"🤝 {self.name} collaborating on: {task}")
        
        # Use AI to understand the task and plan collaboration
        collaboration_prompt = f"""Task: {task}
Other agents available: {', '.join(other_agents)}

How should I, as {self.name}, contribute to this task? What should I ask other agents to do?"""
        
        collaboration_plan = await self.get_ai_response(collaboration_prompt, "Multi-agent collaboration")
        
        logger.info(f"📋 {self.name}'s plan: {collaboration_plan}")
        
        return collaboration_plan
        
    async def run(self):
        """Main run loop"""
        logger.info(f"🚀 Starting {self.name} AI-Powered MCP Agent")
        
        # Display AI status
        if self.groq_client:
            logger.info(f"🤖 AI Enabled: Using Groq LLM (llama3-70b)")
        else:
            logger.info(f"⚠️  AI Disabled: Using intelligent mock responses")
            logger.info(f"   Set GROQ_API_KEY environment variable to enable AI")
        
        try:
            await self.connect_to_coral()
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping {self.name}")
        except Exception as e:
            logger.error(f"Agent error: {e}")


class AIFrontendAgent(AIMCPAgent):
    """AI-powered Frontend Developer Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ai_frontend_001",
            agent_type="frontend",
            name="AI Frontend Developer",
            role_description="an expert frontend developer specializing in React, TypeScript, and modern UI/UX design"
        )
        
    def get_tools(self):
        return [
            {
                "name": "create_react_component",
                "description": "Create a React component with AI-generated code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "component_name": {"type": "string"},
                        "requirements": {"type": "string"}
                    }
                }
            },
            {
                "name": "implement_ui",
                "description": "Implement user interface with AI assistance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "design": {"type": "string"},
                        "features": {"type": "array"}
                    }
                }
            },
            {
                "name": "optimize_performance",
                "description": "Optimize frontend performance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict, ai_suggestion: str) -> Any:
        if tool_name == "create_react_component":
            component_name = arguments.get("component_name", "Component")
            requirements = arguments.get("requirements", "")
            
            # Get AI to generate the component
            prompt = f"Generate a React component named {component_name} with these requirements: {requirements}"
            code = await self.get_ai_response(prompt, "Component generation")
            
            return {
                "success": True,
                "result": f"Created React component: {component_name}",
                "code": code,
                "ai_generated": True
            }
            
        elif tool_name == "implement_ui":
            design = arguments.get("design", "")
            
            prompt = f"Implement a UI based on this design: {design}"
            implementation = await self.get_ai_response(prompt, "UI implementation")
            
            return {
                "success": True,
                "result": "UI implemented with AI assistance",
                "implementation": implementation
            }
            
        return {"success": False, "error": "Unknown tool"}


class AIBackendAgent(AIMCPAgent):
    """AI-powered Backend Developer Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ai_backend_001",
            agent_type="backend",
            name="AI Backend Developer",
            role_description="an expert backend developer specializing in REST APIs, databases, and scalable architecture"
        )
        
    def get_tools(self):
        return [
            {
                "name": "create_api_endpoint",
                "description": "Create a REST API endpoint with AI-generated code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "method": {"type": "string"},
                        "functionality": {"type": "string"}
                    }
                }
            },
            {
                "name": "design_database",
                "description": "Design database schema with AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entities": {"type": "array"},
                        "relationships": {"type": "string"}
                    }
                }
            },
            {
                "name": "implement_auth",
                "description": "Implement authentication system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "auth_type": {"type": "string"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict, ai_suggestion: str) -> Any:
        if tool_name == "create_api_endpoint":
            path = arguments.get("path", "/api/endpoint")
            method = arguments.get("method", "GET")
            functionality = arguments.get("functionality", "")
            
            prompt = f"Create a {method} API endpoint at {path} that {functionality}"
            code = await self.get_ai_response(prompt, "API endpoint generation")
            
            return {
                "success": True,
                "result": f"Created {method} endpoint at {path}",
                "code": code,
                "ai_generated": True
            }
            
        elif tool_name == "design_database":
            entities = arguments.get("entities", [])
            
            prompt = f"Design a database schema for these entities: {', '.join(entities)}"
            schema = await self.get_ai_response(prompt, "Database design")
            
            return {
                "success": True,
                "result": "Database schema designed",
                "schema": schema
            }
            
        return {"success": False, "error": "Unknown tool"}


class AISecurityAgent(AIMCPAgent):
    """AI-powered Security Auditor Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ai_security_001",
            agent_type="security",
            name="AI Security Auditor",
            role_description="a cybersecurity expert specializing in vulnerability assessment, penetration testing, and secure coding practices"
        )
        
    def get_tools(self):
        return [
            {
                "name": "security_audit",
                "description": "Perform AI-powered security audit",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "scope": {"type": "string"}
                    }
                }
            },
            {
                "name": "vulnerability_scan",
                "description": "AI-assisted vulnerability scanning",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"}
                    }
                }
            },
            {
                "name": "security_recommendations",
                "description": "Generate security recommendations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "system": {"type": "string"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict, ai_suggestion: str) -> Any:
        if tool_name == "security_audit":
            target = arguments.get("target", "")
            scope = arguments.get("scope", "comprehensive")
            
            prompt = f"Perform a {scope} security audit on {target}. List potential vulnerabilities."
            audit_results = await self.get_ai_response(prompt, "Security audit")
            
            return {
                "success": True,
                "result": "Security audit completed",
                "findings": audit_results,
                "ai_analysis": True
            }
            
        elif tool_name == "vulnerability_scan":
            code = arguments.get("code", "")
            
            prompt = f"Analyze this code for security vulnerabilities: {code[:500]}"
            vulnerabilities = await self.get_ai_response(prompt, "Vulnerability scan")
            
            return {
                "success": True,
                "result": "Vulnerability scan completed",
                "vulnerabilities": vulnerabilities
            }
            
        return {"success": False, "error": "Unknown tool"}


class AIDevOpsAgent(AIMCPAgent):
    """AI-powered DevOps Engineer Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ai_devops_001",
            agent_type="devops",
            name="AI DevOps Engineer",
            role_description="a DevOps expert specializing in CI/CD pipelines, containerization, infrastructure as code, and cloud deployments"
        )
        
    def get_tools(self):
        return [
            {
                "name": "create_ci_pipeline",
                "description": "Create CI/CD pipeline configuration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "platform": {"type": "string"},
                        "language": {"type": "string"},
                        "requirements": {"type": "string"}
                    }
                }
            },
            {
                "name": "containerize_app",
                "description": "Create Docker/Kubernetes configurations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_type": {"type": "string"},
                        "dependencies": {"type": "array"}
                    }
                }
            },
            {
                "name": "setup_infrastructure",
                "description": "Create infrastructure as code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "provider": {"type": "string"},
                        "resources": {"type": "array"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict, ai_suggestion: str) -> Any:
        if tool_name == "create_ci_pipeline":
            platform = arguments.get("platform", "GitHub Actions")
            language = arguments.get("language", "")
            
            prompt = f"Create a {platform} CI/CD pipeline for {language} application"
            pipeline_config = await self.get_ai_response(prompt, "DevOps pipeline creation")
            
            return {
                "success": True,
                "result": f"Created CI/CD pipeline for {platform}",
                "config": pipeline_config,
                "ai_generated": True
            }
            
        elif tool_name == "containerize_app":
            app_type = arguments.get("app_type", "")
            
            prompt = f"Create Dockerfile and Kubernetes manifests for {app_type} application"
            container_config = await self.get_ai_response(prompt, "Containerization")
            
            return {
                "success": True,
                "result": "Application containerized",
                "config": container_config
            }
            
        elif tool_name == "setup_infrastructure":
            provider = arguments.get("provider", "AWS")
            
            prompt = f"Create infrastructure as code for {provider}"
            iac_config = await self.get_ai_response(prompt, "Infrastructure setup")
            
            return {
                "success": True,
                "result": f"Infrastructure configured for {provider}",
                "config": iac_config
            }
            
        return {"success": False, "error": "Unknown tool"}


class AIDataScientistAgent(AIMCPAgent):
    """AI-powered Data Scientist Agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ai_datascience_001",
            agent_type="datascience",
            name="AI Data Scientist",
            role_description="a data science expert specializing in machine learning, data analysis, visualization, and predictive modeling"
        )
        
    def get_tools(self):
        return [
            {
                "name": "analyze_data",
                "description": "Perform data analysis and insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset": {"type": "string"},
                        "analysis_type": {"type": "string"}
                    }
                }
            },
            {
                "name": "create_ml_model",
                "description": "Create machine learning model",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model_type": {"type": "string"},
                        "problem": {"type": "string"}
                    }
                }
            },
            {
                "name": "data_visualization",
                "description": "Create data visualizations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chart_type": {"type": "string"},
                        "data": {"type": "string"}
                    }
                }
            }
        ]
        
    async def execute_tool(self, tool_name: str, arguments: Dict, ai_suggestion: str) -> Any:
        if tool_name == "analyze_data":
            dataset = arguments.get("dataset", "")
            analysis_type = arguments.get("analysis_type", "exploratory")
            
            prompt = f"Perform {analysis_type} data analysis on {dataset}"
            analysis = await self.get_ai_response(prompt, "Data analysis")
            
            return {
                "success": True,
                "result": f"Data analysis completed",
                "analysis": analysis,
                "ai_generated": True
            }
            
        elif tool_name == "create_ml_model":
            model_type = arguments.get("model_type", "")
            problem = arguments.get("problem", "")
            
            prompt = f"Create {model_type} machine learning model for {problem}"
            model_code = await self.get_ai_response(prompt, "ML model creation")
            
            return {
                "success": True,
                "result": "ML model created",
                "code": model_code
            }
            
        elif tool_name == "data_visualization":
            chart_type = arguments.get("chart_type", "")
            
            prompt = f"Create {chart_type} visualization code using matplotlib/seaborn"
            viz_code = await self.get_ai_response(prompt, "Data visualization")
            
            return {
                "success": True,
                "result": "Visualization created",
                "code": viz_code
            }
            
        return {"success": False, "error": "Unknown tool"}


async def main():
    """Main entry point to run an AI-powered agent"""
    if len(sys.argv) < 2:
        print("Usage: python ai_mcp_agent.py <agent_type>")
        print("Agent types: frontend, backend, security, devops, datascience")
        sys.exit(1)
        
    agent_type = sys.argv[1].lower()
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("\n⚠️  WARNING: GROQ_API_KEY not set!")
        print("   The agent will use intelligent mock responses.")
        print("   To enable AI, set your API key:")
        print("   export GROQ_API_KEY='your_groq_api_key'\n")
    
    if agent_type == "frontend":
        agent = AIFrontendAgent()
    elif agent_type == "backend":
        agent = AIBackendAgent()
    elif agent_type == "security":
        agent = AISecurityAgent()
    elif agent_type == "devops":
        agent = AIDevOpsAgent()
    elif agent_type == "datascience":
        agent = AIDataScientistAgent()
    else:
        print(f"Unknown agent type: {agent_type}")
        sys.exit(1)
        
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())