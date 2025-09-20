#!/usr/bin/env python3
"""
Agent Orchestrator - Manages MCP agent processes and their connection to Coral
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


class AgentOrchestrator:
    """Orchestrates MCP agents and their connection to Coral Server"""
    
    def __init__(self):
        self.coral_url = "http://localhost:5555"
        self.agent_processes = {}
        self.running_agents = []
        
    def check_coral_server(self) -> bool:
        """Check if Coral Server is running"""
        try:
            response = requests.get(f"{self.coral_url}/api/v1/agents", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def start_agent(self, agent_type: str) -> Optional[subprocess.Popen]:
        """Start an MCP agent as a subprocess"""
        agent_script = "/home/linked/Documents/internet-of-agents/ai-dev-squad/coral/agents/mcp_agent_runner.py"
        
        if not os.path.exists(agent_script):
            print(f"❌ Agent script not found: {agent_script}")
            return None
            
        try:
            # Set environment variables
            env = os.environ.copy()
            env["CORAL_SERVER_URL"] = self.coral_url
            env["PYTHONUNBUFFERED"] = "1"  # For real-time output
            
            # Start the agent process
            process = subprocess.Popen(
                [sys.executable, agent_script, agent_type],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                bufsize=1
            )
            
            print(f"✅ Started {agent_type} agent (PID: {process.pid})")
            
            # Store process reference
            self.agent_processes[agent_type] = process
            self.running_agents.append(agent_type)
            
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {agent_type} agent: {e}")
            return None
            
    def stop_agent(self, agent_type: str):
        """Stop a running agent"""
        if agent_type in self.agent_processes:
            process = self.agent_processes[agent_type]
            
            if process.poll() is None:  # Process is still running
                process.terminate()
                time.sleep(1)
                
                if process.poll() is None:  # Still running, force kill
                    process.kill()
                    
                print(f"🛑 Stopped {agent_type} agent")
                
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
            if process.poll() is None:  # Still running
                # Read output without blocking
                try:
                    line = process.stdout.readline()
                    if line:
                        print(f"[{agent_type}] {line.strip()}")
                except:
                    pass
                    
    async def create_collaboration_thread(self, project_name: str) -> Optional[str]:
        """Create a collaboration thread in Coral"""
        thread_data = {
            "name": f"Project: {project_name}",
            "participants": self.running_agents,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "project": project_name
            }
        }
        
        try:
            response = requests.post(
                f"{self.coral_url}/api/v1/threads",
                json=thread_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                thread = response.json()
                return thread.get("id")
            else:
                print(f"Failed to create thread: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None
            
    async def send_task_to_thread(self, thread_id: str, task: str):
        """Send a task to a thread for agents to collaborate on"""
        message_data = {
            "thread_id": thread_id,
            "content": task,
            "sender": "orchestrator",
            "mentions": self.running_agents
        }
        
        try:
            response = requests.post(
                f"{self.coral_url}/api/v1/threads/{thread_id}/messages",
                json=message_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Task sent to thread: {task}")
            else:
                print(f"Failed to send task: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending task: {e}")
            
    def run_interactive_demo(self):
        """Run an interactive demo of multi-agent collaboration"""
        print("\n" + "="*60)
        print("🤖 MULTI-AGENT ORCHESTRATOR - CORAL PROTOCOL")
        print("="*60)
        
        # Check Coral Server
        if not self.check_coral_server():
            print("❌ Coral Server is not running on port 5555")
            print("   Please start it with: cd coral/coral-server-repo && ./gradlew run")
            return
            
        print("✅ Coral Server is running\n")
        
        # Start agents
        print("Starting MCP Agents...")
        print("-"*40)
        
        agents_to_start = ["frontend", "backend", "security"]
        
        for agent_type in agents_to_start:
            process = self.start_agent(agent_type)
            if process:
                time.sleep(2)  # Give agent time to connect
                
        print(f"\n{len(self.running_agents)} agents are now running")
        
        # Monitor and interact
        print("\n📊 Agent Monitor (Press Ctrl+C to stop)")
        print("-"*40)
        
        try:
            while True:
                # Monitor agent output
                self.monitor_agents()
                
                # Check for dead agents and restart
                for agent_type in list(self.agent_processes.keys()):
                    process = self.agent_processes[agent_type]
                    if process.poll() is not None:
                        print(f"⚠️  {agent_type} agent crashed, restarting...")
                        self.start_agent(agent_type)
                        
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nShutting down agents...")
            self.stop_all_agents()
            print("✅ All agents stopped")
            
    async def run_automated_demo(self):
        """Run an automated demo showing agent collaboration"""
        print("\n" + "="*60)
        print("🎬 AUTOMATED MULTI-AGENT COLLABORATION DEMO")
        print("="*60)
        
        # Start agents
        print("\n1️⃣ Starting MCP Agents...")
        agents = ["frontend", "backend", "security"]
        for agent in agents:
            self.start_agent(agent)
            await asyncio.sleep(2)
            
        print(f"   ✅ {len(self.running_agents)} agents running")
        
        # Create collaboration thread
        print("\n2️⃣ Creating Collaboration Thread...")
        thread_id = await self.create_collaboration_thread("E-Commerce Platform")
        
        if thread_id:
            print(f"   ✅ Thread created: {thread_id}")
            
            # Send tasks
            print("\n3️⃣ Sending Tasks to Agents...")
            tasks = [
                "Create user authentication system with JWT",
                "Build product catalog with search functionality",
                "Implement shopping cart and checkout",
                "Perform security audit on authentication"
            ]
            
            for task in tasks:
                print(f"   📋 {task}")
                await self.send_task_to_thread(thread_id, task)
                await asyncio.sleep(3)
                
        # Let agents work
        print("\n4️⃣ Agents Collaborating...")
        print("   (Monitoring for 30 seconds)")
        
        for i in range(30):
            self.monitor_agents()
            await asyncio.sleep(1)
            
        # Clean up
        print("\n5️⃣ Stopping Agents...")
        self.stop_all_agents()
        
        print("\n✅ Demo Complete!")


def main():
    """Main entry point"""
    orchestrator = AgentOrchestrator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run automated demo
        asyncio.run(orchestrator.run_automated_demo())
    else:
        # Run interactive mode
        orchestrator.run_interactive_demo()


if __name__ == "__main__":
    main()