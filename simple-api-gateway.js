const express = require('express');
const app = express();
const port = 8080;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'API Gateway is healthy',
    data: {
      service: 'api-gateway',
      status: 'up',
      port: 8080
    }
  });
});

// Main notification endpoint as per task requirements
app.post('/api/v1/notifications/', (req, res) => {
  const notification = req.body;
  
  res.status(201).json({
    success: true,
    message: 'Notification created successfully',
    data: {
      notification_id: `notif-${Date.now()}`,
      notification_type: notification.notification_type,
      user_id: notification.user_id,
      template_code: notification.template_code,
      status: 'pending',
      request_id: notification.request_id,
      priority: notification.priority || 1,
      created_at: new Date().toISOString()
    }
  });
});

// Status update endpoint
app.post('/api/v1/notifications/status/', (req, res) => {
  const { notification_id, status, timestamp, error } = req.body;
  
  res.json({
    success: true,
    message: 'Notification status updated successfully',
    data: {
      notification_id,
      status,
      timestamp: timestamp || new Date().toISOString(),
      error: error || null
    }
  });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 API Gateway running on port ${port}`);
});