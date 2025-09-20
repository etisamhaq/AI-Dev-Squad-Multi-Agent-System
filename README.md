# 🤖 AI Dev Squad - Coral Multi-Agent System

A revolutionary AI-powered development platform featuring 5 specialized AI agents that collaborate through the Coral Protocol to help with software development tasks. Built for the Internet of Agents Hackathon.

## ✨ Live Demo

- **Chat Interface**: http://localhost:3000
- **Agent Marketplace**: http://localhost:3000/marketplace

## 🚀 Key Features

### 🎯 5 Specialized AI Agents
1. **🎨 Frontend Developer** - Expert in React, TypeScript, UI/UX design
2. **🔧 Backend Developer** - Specializes in REST APIs, databases, cloud services  
3. **🔒 Security Auditor** - Cybersecurity expert, penetration testing, secure coding
4. **🚀 DevOps Engineer** - CI/CD pipelines, containerization, cloud deployments
5. **📊 Data Scientist** - Machine learning, data analysis, visualization

### 🤝 Real AI Integration
- **Groq API** - Lightning-fast LLM responses using Llama 3.3 70B model
- **Intelligent Responses** - Each agent provides specialized, context-aware assistance
- **Real-time Chat** - Interactive conversations with individual or all agents

### 🌊 Coral Protocol Integration
- **MCP Communication** - Agents communicate via Model Context Protocol
- **SSE Connections** - Server-sent events for real-time updates
- **Bridge Server** - Seamless connection between frontend and AI agents

## 🛠️ Technology Stack

### Core System
- **Coral Protocol** - Multi-agent communication framework
- **Groq API** - AI/LLM integration with Llama 3.3
- **Python 3.10+** - AI agent implementation
- **Node.js/Express** - Frontend server

### Components
- **Frontend** - Pure HTML/JavaScript with modern UI
- **Bridge Server** - Flask server connecting frontend to agents
- **Coral Server** - Java/Kotlin MCP protocol server
- **AI Agents** - Python-based intelligent agents

## 📁 Project Structure

```
ai-dev-squad/
├── coral/                        # Core Coral implementation
│   ├── agents/                   # AI agent definitions
│   │   └── ai_mcp_agent.py      # 5 AI agents with Groq integration
│   ├── coral_bridge_server.py   # Bridge API server (Flask)
│   └── coral-server-repo/       # Coral Protocol server
│       
├── frontend/                     # Active frontend
│   ├── index.html               # Main chat interface
│   ├── marketplace.html         # Agent marketplace with embedded chat
│   └── simple-server.js         # Express server
│
└── .env                         # Configuration (API keys)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Java 11+ (for Coral Server)
- Groq API Key

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd ai-dev-squad

# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### 2. Start Coral Server

```bash
# Navigate to Coral server directory
cd coral/coral-server-repo

# Start Coral Protocol server
CONFIG_FILE_PATH=../config.toml \
REGISTRY_FILE_PATH=../registry.toml \
./gradlew run
```

### 3. Start Bridge Server

```bash
# In a new terminal, from project root
python3 coral/coral_bridge_server.py
```

### 4. Start Frontend Server

```bash
# In a new terminal
cd frontend
npm install  # First time only
node simple-server.js
```

### 5. Access the Application

Open your browser and visit:
- **Main Chat**: http://localhost:3000
- **Marketplace**: http://localhost:3000/marketplace

## 💬 How to Use

### Chat Interface
1. Visit http://localhost:3000
2. Select an agent or chat with all agents
3. Type your development question or task
4. Receive intelligent, specialized responses

### Agent Marketplace
1. Visit http://localhost:3000/marketplace
2. Browse the 5 available AI agents
3. Click "Chat with [Agent Name]" to open chat modal
4. Interact directly with that specialized agent

## 🔑 Configuration

### Environment Variables (.env)

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (for extended features)
CORAL_SERVER_URL=http://localhost:5555
```

### Getting a Groq API Key
1. Visit https://console.groq.com
2. Sign up for a free account
3. Generate an API key
4. Add to your .env file

## 📊 System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │────▶│                  │────▶│                 │
│  Frontend       │     │  Bridge Server   │     │  AI Agents      │
│  (HTML/JS)      │     │  (Flask)         │     │  (Python/Groq)  │
│                 │◀────│                  │◀────│                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                         │
                               │                         │
                               ▼                         ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │  Coral Server    │     │   Groq API      │
                        │  (MCP Protocol)  │     │  (Llama 3.3)    │
                        └──────────────────┘     └─────────────────┘
```

## 🎯 Agent Specializations

### Frontend Developer
- React component architecture
- TypeScript best practices
- CSS/Tailwind styling
- Responsive design
- Performance optimization

### Backend Developer
- REST API design
- Database schema design
- Authentication/Authorization
- Microservices architecture
- Cloud services integration

### Security Auditor
- Vulnerability assessment
- Penetration testing strategies
- Secure coding practices
- OWASP compliance
- Security audit reports

### DevOps Engineer
- CI/CD pipeline setup
- Docker containerization
- Kubernetes orchestration
- Infrastructure as Code
- Monitoring and logging

### Data Scientist
- Machine learning models
- Data analysis and visualization
- Statistical analysis
- Python data libraries
- Predictive modeling

## 🔧 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Kill processes on specific ports
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:5001 | xargs kill -9  # Bridge Server
lsof -ti:5555 | xargs kill -9  # Coral Server
```

**Groq API Error**
- Verify your API key in .env file
- Check API rate limits
- Ensure internet connectivity

**No Agent Responses**
- Check Bridge Server is running (port 5001)
- Verify Groq API key is set
- Check terminal for error messages

## 📈 Performance

- **Response Time**: 2-7 seconds per AI response
- **Concurrent Chats**: Supports multiple users
- **Model**: Llama 3.3 70B (via Groq)
- **Availability**: 24/7 local deployment

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional AI agents
- Enhanced UI/UX
- More LLM providers
- Advanced agent collaboration
- Code execution capabilities

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Coral Protocol** - For the MCP agent communication framework
- **Groq** - For lightning-fast LLM inference
- **Meta** - For the Llama 3.3 model
- **Internet of Agents Hackathon** - For the inspiration

## 🚦 Status

✅ **All Systems Operational**
- Coral Server: Running
- Bridge Server: Active
- Frontend: Serving
- AI Agents: Ready
- Groq Integration: Connected

---

Built with ❤️ for the Internet of Agents Hackathon
