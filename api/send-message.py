from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import asyncio
from groq import Groq
import logging

# Add the parent directory to sys.path to import our agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            # Get request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            task = data.get('task', '')
            target_agent = data.get('agent', 'all')

            if not task:
                self.wfile.write(json.dumps({"error": "No task provided"}).encode())
                return

            # Import AI agents
            try:
                from coral.agents.ai_mcp_agent import (
                    AIFrontendAgent, AIBackendAgent, AISecurityAgent,
                    AIDevOpsAgent, AIDataScientistAgent
                )
            except ImportError:
                # Fallback response if import fails
                self.wfile.write(json.dumps({
                    "success": True,
                    "responses": [{
                        "agent": "AI Assistant",
                        "response": f"I'll help you with: {task}",
                        "timestamp": "2025-09-20T12:00:00Z",
                        "is_ai_generated": False
                    }]
                }).encode())
                return

            # Get AI responses
            async def get_responses():
                agents_to_query = []
                if target_agent == 'all':
                    agents_to_query = ['frontend', 'backend', 'security']
                else:
                    agents_to_query = [target_agent]

                responses = []
                for agent_type in agents_to_query:
                    try:
                        if agent_type == 'frontend':
                            agent = AIFrontendAgent()
                        elif agent_type == 'backend':
                            agent = AIBackendAgent()
                        elif agent_type == 'security':
                            agent = AISecurityAgent()
                        elif agent_type == 'devops':
                            agent = AIDevOpsAgent()
                        elif agent_type == 'datascience':
                            agent = AIDataScientistAgent()
                        else:
                            continue

                        ai_response = await agent.get_ai_response(task, "User request")

                        agent_name = {
                            'frontend': 'AI Frontend Developer',
                            'backend': 'AI Backend Developer',
                            'security': 'AI Security Auditor',
                            'devops': 'AI DevOps Engineer',
                            'datascience': 'AI Data Scientist'
                        }.get(agent_type, 'AI Agent')

                        responses.append({
                            "agent": agent_name,
                            "agent_type": agent_type,
                            "response": ai_response,
                            "timestamp": "2025-09-20T12:00:00Z",
                            "is_ai_generated": bool(os.getenv('GROQ_API_KEY'))
                        })

                    except Exception as e:
                        responses.append({
                            "agent": f"AI {agent_type.title()} Developer",
                            "agent_type": agent_type,
                            "response": f"I'll work on: {task}",
                            "timestamp": "2025-09-20T12:00:00Z",
                            "is_ai_generated": False
                        })

                return responses

            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            responses = loop.run_until_complete(get_responses())
            loop.close()

            result = {
                "success": True,
                "target_agent": target_agent,
                "responses": responses
            }

            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
