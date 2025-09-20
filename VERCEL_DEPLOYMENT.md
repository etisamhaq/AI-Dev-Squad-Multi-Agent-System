# 🚀 Deploying AI Dev Squad to Vercel

## Pre-Deployment Setup

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

## Deployment Steps

### 1. Deploy from Project Root
```bash
cd /home/linked/Documents/internet-of-agents/ai-dev-squad
vercel
```

### 2. Configure Environment Variables
In Vercel Dashboard > Settings > Environment Variables:

**Required:**
- `GROQ_API_KEY`: Your Groq API key for AI functionality
- `CORAL_SERVER_URL`: Your Coral server URL (if using external)

**Optional:**
- `NODE_ENV`: production

### 3. Domain Configuration
- Vercel will provide a domain like: `ai-dev-squad.vercel.app`
- You can add custom domains in Vercel dashboard

## Post-Deployment Configuration

### 1. Update API Endpoints
The frontend is already configured to use relative URLs (`window.location.origin`).

### 2. Test Deployment
Visit your Vercel URL and test:
- Main chat: `https://your-app.vercel.app/`
- Marketplace: `https://your-app.vercel.app/marketplace`
- Health check: `https://your-app.vercel.app/api/health`

### 3. Monitor Logs
```bash
vercel logs
```

## Limitations on Vercel

### What Works:
✅ Frontend chat interface
✅ AI agent responses (with Groq API key)
✅ Static file serving
✅ Serverless API functions

### What Doesn't Work:
❌ Coral Protocol server (requires separate deployment)
❌ Real-time SSE connections (limited on serverless)
❌ Background processes (agents run on-demand)

## Alternative Full-Stack Deployment

For complete functionality including Coral Protocol:

### Option 1: Railway/Render
- Deploy entire Python backend
- Supports background processes
- Better for Coral Protocol integration

### Option 2: Docker + Cloud Run
- Containerize entire application
- Deploy on Google Cloud Run or AWS ECS
- Maintains all functionality

### Option 3: Hybrid Approach
- Frontend on Vercel
- Backend on Railway/Render
- Configure CORS for cross-origin requests

## Quick Deploy Commands

```bash
# 1. Navigate to project
cd /home/linked/Documents/internet-of-agents/ai-dev-squad

# 2. Deploy to Vercel
vercel --prod

# 3. Set environment variables
vercel env add GROQ_API_KEY
```

## Troubleshooting

### Common Issues:
1. **API not working**: Check environment variables in Vercel dashboard
2. **Import errors**: Ensure all dependencies in api/requirements.txt
3. **CORS errors**: Verify API functions have CORS headers

### Debug Commands:
```bash
vercel logs --follow
vercel dev  # Test locally
```

Your AI Dev Squad will be live at: `https://your-app.vercel.app` 🚀
