const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000;

// Serve static files
app.use(express.static('public'));
app.use(express.static('.'));

// Main route - serve the new simplified AI agent chat
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Marketplace route - serve the new marketplace with 5 real agents
app.get('/marketplace', (req, res) => {
  res.sendFile(path.join(__dirname, 'marketplace.html'));
});

// Coral integrated page
app.get('/coral', (req, res) => {
  res.sendFile(path.join(__dirname, 'coral-integrated.html'));
});

// Enhanced UI page
app.get('/enhanced', (req, res) => {
  res.sendFile(path.join(__dirname, 'enhanced-ui.html'));
});

// Live Coral Integration page
app.get('/coral-live', (req, res) => {
  res.sendFile(path.join(__dirname, 'coral-live.html'));
});

// Real Agent Integration page
app.get('/coral-real', (req, res) => {
  res.sendFile(path.join(__dirname, 'coral-real.html'));
});

// Test page route
app.get('/test', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'test.html'));
});

// Removed API proxy route due to Express 5 compatibility issues

app.listen(PORT, () => {
  console.log(`
========================================
🚀 AI Dev Squad Frontend Server
========================================
✅ Server running on http://localhost:${PORT}
📊 Test page: http://localhost:${PORT}/test
🔗 Backend API: http://localhost:8000/api/v1/
========================================
Note: Using Express server as Next.js has bus error issues on this system
  `);
});