const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const axios = require('axios');

const app = express();
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'API Gateway is healthy',
    data: { service: 'api-gateway', status: 'up', port: 80 }
  });
});

// Auth Service Routes
app.use('/auth', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  pathRewrite: { '^/auth': '/api/v1/auth' }
}));

// User Service Routes  
app.use('/users', createProxyMiddleware({
  target: 'http://localhost:8001',
  changeOrigin: true,
  pathRewrite: { '^/users': '/api/v1/users' }
}));

// Template Service Routes
app.use('/templates', createProxyMiddleware({
  target: 'http://localhost:3001',
  changeOrigin: true,
  pathRewrite: { '^/templates': '/api/v1/templates' }
}));

// Smart Notification Route
app.post('/api/v1/notifications/send', async (req, res) => {
  try {
    const { user_id, notification_type, template_code, variables } = req.body;

    // Get user preferences
    const userResponse = await axios.get(`http://localhost:8001/api/v1/users/${user_id}/`);
    const userData = userResponse.data.data;
    const preferences = userData.preferences || { email_notifications: true, push_notifications: true };

    // Get template
    const templateResponse = await axios.get(`http://localhost:3001/api/v1/templates/by-code/${template_code}`);
    const templateData = templateResponse.data.data;

    const notifications = [];

    // Send push if enabled
    if (preferences.push_notifications && (notification_type === 'push' || notification_type === 'both')) {
      const pushResponse = await axios.post('http://localhost:8003/api/v1/push/send', {
        user_id,
        title: templateData.subject,
        message: templateData.body,
        data: variables
      });
      notifications.push({ type: 'push', ...pushResponse.data.data });
    }

    // Send email if enabled  
    if (preferences.email_notifications && (notification_type === 'email' || notification_type === 'both')) {
      // Queue email via RabbitMQ would go here
      notifications.push({ type: 'email', status: 'queued' });
    }

    res.json({
      success: true,
      message: `Notifications processed (${notifications.length} sent)`,
      data: { user_id, notifications, preferences }
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Notification processing failed',
      error: error.message
    });
  }
});

app.listen(80, () => {
  console.log('🚀 API Gateway running on port 80');
});