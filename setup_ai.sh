#!/bin/bash

# AI Dev Squad - AI Setup Script
# Sets up Groq API key and starts AI-powered agents

echo "============================================================"
echo "🤖 AI DEV SQUAD - GROQ LLM SETUP"
echo "============================================================"
echo ""

# Check if Groq API key is already set
if [ -n "$GROQ_API_KEY" ]; then
    echo "✅ Groq API key is already configured"
    echo "   Current key: ${GROQ_API_KEY:0:10}..."
else
    echo "⚠️  Groq API key not found"
    echo ""
    echo "To get a Groq API key:"
    echo "1. Visit https://console.groq.com/keys"
    echo "2. Sign up or log in"
    echo "3. Create a new API key"
    echo ""
    read -p "Enter your Groq API key (or press Enter to skip): " api_key
    
    if [ -n "$api_key" ]; then
        export GROQ_API_KEY="$api_key"
        echo "✅ Groq API key set for this session"
        
        # Ask if user wants to save it permanently
        read -p "Save API key to ~/.bashrc? (y/n): " save_key
        if [ "$save_key" = "y" ] || [ "$save_key" = "Y" ]; then
            echo "export GROQ_API_KEY='$api_key'" >> ~/.bashrc
            echo "✅ API key saved to ~/.bashrc"
        fi
    else
        echo "⚠️  Continuing without AI (using mock responses)"
    fi
fi

echo ""
echo "============================================================"
echo "🚀 STARTING AI AGENTS"
echo "============================================================"
echo ""

# Check if Coral Server is running
if curl -s http://localhost:5555/api/v1/agents > /dev/null 2>&1; then
    echo "✅ Coral Server is running"
else
    echo "❌ Coral Server is not running"
    echo "   Please start it in another terminal:"
    echo "   cd coral/coral-server-repo && ./gradlew run"
    exit 1
fi

# Kill any existing agent processes
echo "Cleaning up old agent processes..."
pkill -f "ai_mcp_agent.py" 2>/dev/null
pkill -f "mcp_agent_runner.py" 2>/dev/null

# Start the AI agent orchestrator
echo ""
echo "Starting AI Agent Orchestrator..."
echo "----------------------------------------"

if [ -n "$GROQ_API_KEY" ]; then
    echo "🧠 AI Mode: ENABLED (using Groq LLM)"
else
    echo "📝 AI Mode: DISABLED (using mock responses)"
fi

echo ""
echo "Starting agents..."
python3 coral/ai_agent_orchestrator.py