#!/usr/bin/env python3
"""
Complete Coral Protocol Integration Demo
Shows MCP agents connecting to Coral Server and communicating
"""

import asyncio
import sys
import os
import subprocess
import signal
import time
from datetime import datetime

# Add parent directory to path
sys.path.append('/home/linked/Documents/internet-of-agents/ai-dev-squad')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from agents.models import Agent


class CoralDemo:
    """Demonstrates full Coral Protocol integration"""
    
    def __init__(self):
        self.processes = []
        self.coral_url = "http://localhost:5555"
        
    def check_services(self):
        """Check if required services are running"""
        import requests
        
        print("\n🔍 Checking Services...")
        print("-" * 50)
        
        services = {
            "Django Backend": "http://localhost:8000/api/v1/agents/",
            "Coral Server": "http://localhost:5555/api/v1/agents",
            "Frontend": "http://localhost:3000"
        }
        
        all_ok = True
        for name, url in services.items():
            try:
                requests.get(url, timeout=2)
                print(f"✅ {name}: Running")
            except:
                print(f"❌ {name}: Not running")
                if name == "Coral Server":
                    all_ok = False
                    
        return all_ok
        
    def start_agent_process(self, agent_type):
        """Start an MCP agent as a subprocess"""
        script_path = "/home/linked/Documents/internet-of-agents/ai-dev-squad/coral/agents/mcp_agent_runner.py"
        
        print(f"  • Starting {agent_type} agent...")
        
        env = os.environ.copy()
        env["CORAL_SERVER_URL"] = self.coral_url
        env["PYTHONUNBUFFERED"] = "1"
        
        process = subprocess.Popen(
            [sys.executable, script_path, agent_type],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True
        )
        
        self.processes.append(process)
        print(f"    ✅ Started (PID: {process.pid})")
        
        return process
        
    def stop_all_processes(self):
        """Stop all agent processes"""
        print("\n🛑 Stopping all agents...")
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                time.sleep(0.5)
                if process.poll() is None:
                    process.kill()
        print("✅ All agents stopped")
        
    def run_demo(self):
        """Run the complete demo"""
        print("\n" + "=" * 60)
        print("🚀 CORAL PROTOCOL INTEGRATION DEMO")
        print("=" * 60)
        
        try:
            # Check services
            if not self.check_services():
                print("\n⚠️  Coral Server must be running!")
                print("   Start it with: cd coral/coral-server-repo && ./gradlew run")
                return
                
            # Start MCP agents
            print("\n🤖 Starting MCP Agents...")
            print("-" * 50)
            
            agents = ["frontend", "backend", "security"]
            for agent_type in agents:
                self.start_agent_process(agent_type)
                time.sleep(1)  # Give each agent time to connect
                
            print(f"\n✅ {len(agents)} MCP agents are now running and connected to Coral")
            
            # Display info
            print("\n" + "=" * 60)
            print("📊 SYSTEM STATUS")
            print("=" * 60)
            print(f"• Coral Server: Running on port 5555")
            print(f"• Active Agents: {len(agents)}")
            print(f"• Agent Types: {', '.join(agents)}")
            print(f"• Connection: SSE (Server-Sent Events)")
            print(f"• Protocol: MCP (Model Context Protocol)")
            
            print("\n" + "=" * 60)
            print("🌐 ACCESS POINTS")
            print("=" * 60)
            print("• Live Dashboard: http://localhost:3000/coral-live")
            print("• Coral Integration: http://localhost:3000/coral")
            print("• Enhanced UI: http://localhost:3000/enhanced")
            print("• Django API: http://localhost:8000/api/v1/")
            print("• Coral API: http://localhost:5555/api/v1/")
            
            print("\n" + "=" * 60)
            print("💡 WHAT'S HAPPENING")
            print("=" * 60)
            print("1. MCP agents are connected to Coral Server via SSE")
            print("2. Agents can receive and process tool calls")
            print("3. Agents can communicate through Coral threads")
            print("4. Frontend can display real-time agent status")
            print("5. System is ready for multi-agent collaboration")
            
            print("\n" + "=" * 60)
            print("🎯 NEXT STEPS")
            print("=" * 60)
            print("1. Open http://localhost:3000/coral-live in browser")
            print("2. Click 'Start Agents' to see live connections")
            print("3. Send tasks to agents for collaboration")
            print("4. Watch real-time message exchange")
            
            # Keep running and monitor
            print("\n📡 Monitoring agents (Press Ctrl+C to stop)...")
            print("-" * 50)
            
            while True:
                # Check if agents are still running
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        agent_type = agents[i] if i < len(agents) else "unknown"
                        print(f"⚠️  {agent_type} agent stopped (exit code: {process.poll()})")
                        
                        # Restart the agent
                        print(f"  🔄 Restarting {agent_type} agent...")
                        self.processes[i] = self.start_agent_process(agent_type)
                        
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal...")
        finally:
            self.stop_all_processes()
            print("\n✨ Demo complete!")


def main():
    """Main entry point"""
    demo = CoralDemo()
    demo.run_demo()


if __name__ == "__main__":
    # Handle signals properly
    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    main()