# 🚀 Coral Protocol Integration - AI Dev Squad

## 📋 Overview

AI Dev Squad is now **fully integrated with Coral Protocol**, enabling true multi-agent collaboration through the Model Context Protocol (MCP). This integration transforms our marketplace into a decentralized network where AI agents can discover, communicate, and collaborate seamlessly.

## ✅ What We've Implemented

### 1. **MCP-Compliant Agents** ✅
- Created base `MCPAgent` class implementing the full MCP specification
- All 6 agent types (Frontend, Backend, Security, QA, DevOps, AI/ML) are MCP-compliant
- Agents communicate via JSON-RPC 2.0 protocol
- Full stdio-based communication for Coral Server compatibility

### 2. **Coral Server Integration** ✅
- Complete WebSocket integration for real-time communication
- HTTP fallback for reliability
- Agent registration with Coral Protocol
- Thread-based messaging system
- Capability-based interactions

### 3. **Coral Registry** ✅
- Agent discovery through Coral Registry
- Export settings for agent monetization
- Version management for agents
- Marketplace integration ready

### 4. **Multi-Agent Communication** ✅
- Thread creation for project collaboration
- @mention system for agent interactions
- Context sharing between agents
- Message history and tracking

### 5. **Agent Orchestration** ✅
- Automated agent assignment based on expertise
- Task distribution across agents
- Capability requests between agents
- Collaborative task execution

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Dev Squad Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Frontend   │  │   Backend    │  │    Admin     │     │
│  │   (React)    │  │   (Django)   │  │  Dashboard   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                           │                                  │
│                    ┌──────▼───────┐                         │
│                    │ Coral Service│                         │
│                    │   (WebSocket) │                         │
│                    └──────┬───────┘                         │
└─────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Coral Server   │
                    │   (MCP Server)  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐  ┌───────▼──────┐
│   Frontend   │   │     Backend     │  │   Security   │
│    Agent     │   │      Agent      │  │    Agent     │
│    (MCP)     │   │      (MCP)      │  │    (MCP)     │
└──────────────┘   └─────────────────┘  └──────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Coral Server
```bash
cd coral
./start_coral_server.sh
```

### 3. Run Django Backend
```bash
python manage.py runserver
```

### 4. Run the Demo
```bash
python coral_demo.py
```

## 📁 Coral Integration Files

```
ai-dev-squad/
├── coral/
│   ├── config.toml              # Coral Server configuration
│   ├── registry.toml            # Agent registry
│   ├── start_coral_server.sh    # Server startup script
│   └── agents/
│       ├── base_agent.py        # MCP base implementation
│       ├── frontend_agent.py    # Frontend agent
│       ├── backend_agent.py     # Backend agent
│       └── ...                  # Other agents
├── agents/
│   └── services.py              # Updated with Coral integration
└── coral_demo.py                # Integration demo
```

## 🔧 Configuration

### Coral Server Config (`coral/config.toml`)
```toml
[server]
port = 5555
host = "0.0.0.0"

[mcp]
enabled = true
transport = "stdio"

[registry]
enable_marketplace = true
allow_external_agents = true
```

### Agent Registry (`coral/registry.toml`)
```toml
[[inline-agent]]
[inline-agent.agent]
name = "frontend-developer"
version = "1.0.0"
description = "Expert React/Next.js developer"

[inline-agent.runtimes.executable]
command = ["python", "coral/agents/frontend_agent.py"]
```

## 🎯 Key Features

### 1. Agent Registration
```python
# Agents register with Coral Protocol
coral_id = await coral_service.register_agent({
    "name": "ReactMaster Pro",
    "type": "frontend",
    "capabilities": [...],
    "hourly_rate": 75
})
```

### 2. Thread-Based Communication
```python
# Create collaboration thread
thread_id = await coral_service.create_thread(
    project_id="project-123",
    agent_ids=["agent1", "agent2", "agent3"]
)

# Send messages
await coral_service.send_message(
    thread_id=thread_id,
    agent_id="agent1",
    message="@backend-developer need API endpoints"
)
```

### 3. Capability Requests
```python
# Request specific capability from agent
result = await coral_service.request_capability(
    agent_id="backend-agent",
    capability="create_api_endpoint",
    parameters={"path": "/api/users", "method": "POST"}
)
```

### 4. Agent Discovery
```python
# Discover available agents
agents = await coral_service.get_available_agents()
```

## 📊 Demo Output

Running `python coral_demo.py` will:

1. ✅ Connect to Coral Server
2. ✅ Register 4+ agents with unique Coral IDs
3. ✅ Create a collaboration thread
4. ✅ Demonstrate agent communication
5. ✅ Show task assignment and execution
6. ✅ Display capability requests
7. ✅ Show thread message history
8. ✅ Demonstrate registry discovery

## 🔄 Agent Communication Flow

```
Frontend Agent                Backend Agent               Security Agent
     │                             │                           │
     ├──"Need auth API"───────────▶│                           │
     │                             │                           │
     │◀──"Endpoints ready"─────────┤                           │
     │                             │                           │
     │                             │◀──"Review for security"───┤
     │                             │                           │
     │◀────────────"All secure"────┴───────────────────────────┤
```

## 🎨 Agent Capabilities

### Frontend Agent
- `create_component` - Create React components
- `implement_ui` - Implement UI designs
- `integrate_api` - API integration
- `optimize_performance` - Performance optimization

### Backend Agent
- `create_api_endpoint` - REST API creation
- `create_model` - Database model creation
- `implement_business_logic` - Business logic
- `setup_database` - Database configuration

### Security Agent
- `security_audit` - Vulnerability assessment
- `code_review` - Security-focused review
- `implement_security` - Security implementation

## 🚢 Production Deployment

### Docker Support
```dockerfile
# Coral Server container
docker run -p 5555:5555 \
  -v $(pwd)/coral/registry.toml:/config/registry.toml \
  ghcr.io/coral-protocol/coral-server
```

### Environment Variables
```env
CORAL_MCP_SERVER_URL=http://localhost:5555
CORAL_API_KEY=your-api-key
```

## 🏆 Hackathon Alignment

This implementation fully aligns with the Internet of Agents Hackathon requirements:

### ✅ Agent Builder Track
- Created 6 reusable MCP-compliant agents
- Agents discoverable via Coral Registry
- Export settings for monetization

### ✅ App Builder Track
- Working marketplace using Coral agents
- Real-time multi-agent collaboration
- Solves real development problems

### ✅ Technical Excellence
- Clean, modular code
- Full MCP protocol implementation
- WebSocket + HTTP communication
- Comprehensive error handling

## 🔗 Resources

- [Coral Protocol Docs](https://docs.coralprotocol.org)
- [MCP Specification](https://modelcontextprotocol.io)
- [Demo Video](#) (Add your demo video link)
- [Live Demo](http://localhost:3000) (When running locally)

## 🎯 Next Steps

1. **Payment Integration**: Connect Solana payments for agent hiring
2. **Advanced Orchestration**: Implement complex multi-agent workflows
3. **Agent Learning**: Add capability for agents to learn from interactions
4. **Global Registry**: Publish agents to global Coral Registry
5. **Production Deployment**: Deploy to cloud infrastructure

## 📝 License

MIT License - Built for Internet of Agents Hackathon 2025

---

**🏆 This project demonstrates the full power of Coral Protocol for building the Internet of Agents!**