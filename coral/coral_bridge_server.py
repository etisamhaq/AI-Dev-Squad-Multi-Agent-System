#!/usr/bin/env python3
"""
Coral Bridge Server - Connects frontend to real MCP agents via Coral
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import aiohttp
import json
import os
import sys
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append('/home/linked/Documents/internet-of-agents/ai-dev-squad')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global storage for messages and agent status
agent_messages = []
active_agents = []
coral_url = "http://localhost:5555"


@app.route('/api/agents/status', methods=['GET'])
def get_agent_status():
    """Get status of all agents"""
    try:
        # Check Coral for connected agents
        response = requests.get(f"{coral_url}/api/v1/agents")
        coral_agents = response.json() if response.status_code == 200 else []
        
        # Check for running processes (simplified check)
        import subprocess
        result = subprocess.run(
            "ps aux | grep -E '(ai_mcp_agent|mcp_agent_runner)' | grep -v grep | wc -l",
            shell=True,
            capture_output=True,
            text=True
        )
        running_count = int(result.stdout.strip())
        
        return jsonify({
            "coral_connected": len(coral_agents),
            "processes_running": running_count,
            "agents": active_agents,
            "status": "connected" if running_count > 0 else "disconnected"
        })
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/start', methods=['POST'])
def start_agents():
    """Start AI agents"""
    global active_agents
    
    try:
        import subprocess
        
        # Start AI agents
        agent_types = ['frontend', 'backend', 'security']
        started = []
        
        for agent_type in agent_types:
            # Start each agent
            script_path = "/home/linked/Documents/internet-of-agents/ai-dev-squad/coral/agents/ai_mcp_agent.py"
            
            env = os.environ.copy()
            env["CORAL_SERVER_URL"] = coral_url
            
            # Pass Groq API key if available
            if os.getenv("GROQ_API_KEY"):
                env["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
            
            process = subprocess.Popen(
                [sys.executable, script_path, agent_type],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True
            )
            
            started.append({
                "type": agent_type,
                "id": f"ai_{agent_type}_001",
                "pid": process.pid,
                "status": "connected"
            })
            
        active_agents = started
        
        return jsonify({
            "success": True,
            "agents_started": len(started),
            "agents": started
        })
        
    except Exception as e:
        logger.error(f"Error starting agents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/stop', methods=['POST'])
def stop_agents():
    """Stop all agents"""
    global active_agents
    
    try:
        import subprocess
        
        # Kill agent processes
        subprocess.run("pkill -f 'ai_mcp_agent.py'", shell=True)
        subprocess.run("pkill -f 'mcp_agent_runner.py'", shell=True)
        
        active_agents = []
        
        return jsonify({
            "success": True,
            "message": "All agents stopped"
        })
        
    except Exception as e:
        logger.error(f"Error stopping agents: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send a message to specific agent(s) with real AI response"""
    global agent_messages
    
    try:
        data = request.json
        task = data.get('task', '')
        sender = data.get('sender', 'user')
        target_agent = data.get('agent', 'all')  # Can be 'frontend', 'backend', 'security', or 'all'
        
        if not task:
            return jsonify({"error": "No task provided"}), 400
        
        # Store the message
        message = {
            "id": len(agent_messages) + 1,
            "sender": sender,
            "content": task,
            "target_agent": target_agent,
            "timestamp": datetime.now().isoformat(),
            "responses": []
        }
        agent_messages.append(message)
        
        # Import AI agent modules for real responses
        import sys
        sys.path.append('/home/linked/Documents/internet-of-agents/ai-dev-squad/coral/agents')
        from ai_mcp_agent import (AIFrontendAgent, AIBackendAgent, AISecurityAgent,
                                  AIDevOpsAgent, AIDataScientistAgent)
        
        async def get_ai_response(agent_type, task):
            """Get real AI response from agent"""
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
                return None
                
            response = await agent.get_ai_response(task, "User request")
            return response
            
        # Determine which agents to query
        agents_to_query = []
        if target_agent == 'all':
            agents_to_query = ['frontend', 'backend', 'security']
        else:
            agents_to_query = [target_agent]
            
        # Get real AI responses
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent_responses = []
        for agent_type in agents_to_query:
            try:
                # Get real AI response
                ai_response = loop.run_until_complete(get_ai_response(agent_type, task))
                
                agent_name = {
                    'frontend': 'AI Frontend Developer',
                    'backend': 'AI Backend Developer',
                    'security': 'AI Security Auditor',
                    'devops': 'AI DevOps Engineer',
                    'datascience': 'AI Data Scientist'
                }.get(agent_type, 'AI Agent')
                
                if ai_response:
                    agent_responses.append({
                        "agent": agent_name,
                        "agent_type": agent_type,
                        "response": ai_response,
                        "timestamp": datetime.now().isoformat(),
                        "is_ai_generated": True
                    })
                else:
                    # Fallback response
                    agent_responses.append({
                        "agent": agent_name,
                        "agent_type": agent_type,
                        "response": f"I'll help with: {task}",
                        "timestamp": datetime.now().isoformat(),
                        "is_ai_generated": False
                    })
            except Exception as e:
                logger.error(f"Error getting AI response from {agent_type}: {e}")
                # Add fallback response on error
                agent_responses.append({
                    "agent": f"AI {agent_type.title()} Developer",
                    "agent_type": agent_type,
                    "response": f"I'll work on: {task}",
                    "timestamp": datetime.now().isoformat(),
                    "is_ai_generated": False
                })
        
        loop.close()
        
        message["responses"] = agent_responses
        
        return jsonify({
            "success": True,
            "message_id": message["id"],
            "target_agent": target_agent,
            "responses": agent_responses
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages and responses"""
    return jsonify({
        "messages": agent_messages,
        "count": len(agent_messages)
    })


@app.route('/api/messages/<int:message_id>/responses', methods=['GET'])
def get_message_responses(message_id):
    """Get responses for a specific message"""
    message = next((m for m in agent_messages if m["id"] == message_id), None)
    
    if not message:
        return jsonify({"error": "Message not found"}), 404
        
    # In a real implementation, this would fetch actual agent responses from Coral
    return jsonify({
        "message_id": message_id,
        "responses": message.get("responses", [])
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "coral-bridge"})


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌉 CORAL BRIDGE SERVER")
    print("=" * 60)
    print("Connecting frontend to real MCP agents...")
    print(f"Bridge API: http://localhost:5001")
    print(f"Coral Server: {coral_url}")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)