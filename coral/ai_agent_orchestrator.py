#!/usr/bin/env python3
"""
AI Agent Orchestrator - Manages AI-powered MCP agents with Groq LLM
"""

import os
import sys
import json
import asyncio
import subprocess
import signal
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append('/home/linked/Documents/internet-of-agents/ai-dev-squad')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from agents.models import Agent


class AIAgentOrchestrator:
    """Orchestrates AI-powered MCP agents with Groq LLM integration"""
    
    def __init__(self):
        self.coral_url = "http://localhost:5555"
        self.agent_processes = {}
        self.running_agents = []
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
    def check_services(self) -> bool:
        """Check if required services are running"""
        print("\n🔍 Checking Services Status...")
        print("-" * 50)
        
        services = {
            "Coral Server": f"{self.coral_url}/api/v1/agents",
            "Django Backend": "http://localhost:8000/api/v1/agents/",
            "Frontend": "http://localhost:3000"
        }
        
        all_running = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=2)
                print(f"✅ {name}: Running")
            except:
                print(f"❌ {name}: Not running")
                if name == "Coral Server":
                    all_running = False
                    
        # Check Groq API key
        if self.groq_api_key:
            print(f"✅ Groq API: Configured (AI enabled)")
        else:
            print(f"⚠️  Groq API: Not configured (using mock responses)")
            print(f"   Set GROQ_API_KEY to enable AI capabilities")
                    
        return all_running
        
    def start_ai_agent(self, agent_type: str) -> Optional[subprocess.Popen]:
        """Start an AI-powered MCP agent"""
        # Use the new AI agent script
        agent_script = "/home/linked/Documents/internet-of-agents/ai-dev-squad/coral/agents/ai_mcp_agent.py"
        
        if not os.path.exists(agent_script):
            print(f"❌ AI agent script not found: {agent_script}")
            return None
            
        try:
            # Set environment variables
            env = os.environ.copy()
            env["CORAL_SERVER_URL"] = self.coral_url
            env["PYTHONUNBUFFERED"] = "1"
            
            # Pass Groq API key if available
            if self.groq_api_key:
                env["GROQ_API_KEY"] = self.groq_api_key
            
            # Start the agent process
            process = subprocess.Popen(
                [sys.executable, agent_script, agent_type],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                bufsize=1
            )
            
            print(f"✅ Started AI {agent_type} agent (PID: {process.pid})")
            
            # Store process reference
            self.agent_processes[agent_type] = process
            self.running_agents.append(agent_type)
            
            return process
            
        except Exception as e:
            print(f"❌ Failed to start AI {agent_type} agent: {e}")
            return None
            
    def stop_agent(self, agent_type: str):
        """Stop a running agent"""
        if agent_type in self.agent_processes:
            process = self.agent_processes[agent_type]
            
            if process.poll() is None:
                process.terminate()
                time.sleep(1)
                
                if process.poll() is None:
                    process.kill()
                    
                print(f"🛑 Stopped AI {agent_type} agent")
                
            del self.agent_processes[agent_type]
            if agent_type in self.running_agents:
                self.running_agents.remove(agent_type)
                
    def stop_all_agents(self):
        """Stop all running agents"""
        for agent_type in list(self.agent_processes.keys()):
            self.stop_agent(agent_type)
            
    def monitor_agents(self):
        """Monitor agent output"""
        for agent_type, process in self.agent_processes.items():
            if process.poll() is None:
                try:
                    line = process.stdout.readline()
                    if line:
                        print(f"[AI-{agent_type}] {line.strip()}")
                except:
                    pass
                    
    async def demonstrate_ai_collaboration(self):
        """Demonstrate AI agents collaborating on a task"""
        print("\n" + "=" * 60)
        print("🤖 AI AGENT COLLABORATION DEMO")
        print("=" * 60)
        
        # Example tasks to demonstrate
        tasks = [
            "Build a user authentication system with JWT tokens",
            "Create a product catalog with search and filtering",
            "Implement a shopping cart with payment processing"
        ]
        
        print("\nAI Agents will collaborate on these tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task}")
            
        print("\n📋 Starting collaboration...")
        print("-" * 50)
        
        # Simulate task distribution (in real scenario, this would go through Coral)
        for task in tasks:
            print(f"\n🎯 Task: {task}")
            print("   Frontend Agent: Planning UI components...")
            print("   Backend Agent: Designing API endpoints...")
            print("   Security Agent: Preparing security audit...")
            time.sleep(2)
            
    def run_interactive_demo(self):
        """Run an interactive demo with AI agents"""
        print("\n" + "=" * 60)
        print("🤖 AI-POWERED MULTI-AGENT ORCHESTRATOR")
        print("=" * 60)
        
        # Check services
        if not self.check_services():
            print("\n⚠️  Coral Server is not running on port 5555")
            print("   Please start it with: cd coral/coral-server-repo && ./gradlew run")
            return
            
        print("\n✅ All services ready")
        
        # Display AI status
        print("\n" + "=" * 60)
        print("🧠 AI CAPABILITIES STATUS")
        print("=" * 60)
        
        if self.groq_api_key:
            print("✅ Groq LLM: ENABLED")
            print("   Model: Llama 3 70B")
            print("   Agents will use real AI for responses")
        else:
            print("⚠️  Groq LLM: DISABLED")
            print("   Using intelligent mock responses")
            print("\n   To enable AI:")
            print("   export GROQ_API_KEY='your_groq_api_key'")
            
        # Start AI agents
        print("\n" + "=" * 60)
        print("🚀 Starting AI-Powered MCP Agents")
        print("=" * 60)
        
        agents_to_start = ["frontend", "backend", "security"]
        
        for agent_type in agents_to_start:
            process = self.start_ai_agent(agent_type)
            if process:
                time.sleep(2)
                
        print(f"\n✅ {len(self.running_agents)} AI agents are now running")
        
        # Display access points
        print("\n" + "=" * 60)
        print("🌐 ACCESS POINTS")
        print("=" * 60)
        print("• Live Dashboard: http://localhost:3000/coral-live")
        print("• Coral Integration: http://localhost:3000/coral")
        print("• Enhanced UI: http://localhost:3000/enhanced")
        
        print("\n" + "=" * 60)
        print("💡 AI AGENT CAPABILITIES")
        print("=" * 60)
        print("• Frontend Agent: React components, UI/UX design")
        print("• Backend Agent: REST APIs, database design")  
        print("• Security Agent: Vulnerability assessment, auditing")
        
        # Monitor and interact
        print("\n📡 Monitoring AI agents (Press Ctrl+C to stop)...")
        print("-" * 50)
        
        try:
            while True:
                self.monitor_agents()
                
                # Check for dead agents and restart
                for agent_type in list(self.agent_processes.keys()):
                    process = self.agent_processes[agent_type]
                    if process.poll() is not None:
                        print(f"⚠️  AI {agent_type} agent crashed, restarting...")
                        self.start_ai_agent(agent_type)
                        
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nShutting down AI agents...")
            self.stop_all_agents()
            print("✅ All AI agents stopped")


def main():
    """Main entry point"""
    orchestrator = AIAgentOrchestrator()
    
    # Check if API key is provided as argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            asyncio.run(orchestrator.demonstrate_ai_collaboration())
        elif sys.argv[1].startswith("GROQ_API_KEY="):
            os.environ["GROQ_API_KEY"] = sys.argv[1].split("=", 1)[1]
            orchestrator.groq_api_key = os.environ["GROQ_API_KEY"]
            print(f"✅ Groq API key set")
            orchestrator.run_interactive_demo()
        else:
            print("Usage: python ai_agent_orchestrator.py [demo | GROQ_API_KEY=your_key]")
    else:
        orchestrator.run_interactive_demo()


if __name__ == "__main__":
    main()