const { v4: uuidv4 } = require('uuid');

class NotificationController {
  
  // POST /notifications - Create notification (for testing)
  async create(req, res) {
    try {
      const { type, recipient, subject, message } = req.body;
      
      if (!type || !recipient || !message) {
        return res.status(400).json({
          error: 'Missing required fields: type, recipient, message'
        });
      }

      const notification = {
        id: uuidv4(),
        type,
        recipient,
        subject: subject || '',
        message,
        status: 'PENDING',
        createdAt: new Date()
      };

      // Simuler l'envoi
      notification.status = 'SENT';

      res.status(201).json({
        message: 'Notification created',
        notification
      });

    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  // GET /notifications/:id - Get notification by ID
  async getById(req, res) {
    try {
      const { id } = req.params;
      
      // Simulation de récupération depuis MongoDB
      const notification = {
        id,
        type: 'EMAIL',
        recipient: 'pat-001',
        subject: 'Confirmation RDV',
        message: 'Votre rendez-vous est confirmé',
        status: 'SENT',
        createdAt: new Date()
      };

      if (!notification) {
        return res.status(404).json({ error: 'Notification not found' });
      }

      res.json(notification);

    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
}

module.exports = new NotificationController();
