const mongoose = require('mongoose');

// Define Notification Schema for MongoDB
const notificationSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  type: { type: String, required: true },
  recipient: { type: String, required: true },
  subject: { type: String },
  message: { type: String, required: true },
  status: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

// In-memory store for simulation (when MongoDB is not connected)
const notificationStore = new Map();

class NotificationService {
  
  /**
   * Process appointment scheduled event with transaction handling
   */
  async sendConfirmation(appointment) {
    const session = await mongoose.startSession();
    
    try {
      session.startTransaction();
      
      console.log(`[Notification] Starting transaction for confirmation: ${appointment.id}`);
      
      // Create notification record
      const notification = {
        id: `notif-${Date.now()}`,
        type: 'EMAIL',
        recipient: appointment.patientId,
        subject: `Confirmation RDV - ${appointment.specialty}`,
        message: `Votre rendez-vous est confirmé pour le ${new Date(appointment.dateTime).toLocaleString()}`,
        status: 'PENDING',
        createdAt: new Date()
      };

      // Save notification to store (simulating MongoDB)
      notificationStore.set(notification.id, notification);
      
      // Simulate sending email (external API call)
      notification.status = 'SENT';
      notificationStore.set(notification.id, notification);
      
      // Commit transaction
      await session.commitTransaction();
      session.endSession();
      
      console.log(`[Notification] Transaction committed: Email sent to ${appointment.patientId}`);
      return notification;
      
    } catch (error) {
      // Abort transaction on error
      await session.abortTransaction();
      session.endSession();
      console.error(`[Notification] Transaction failed:`, error.message);
      throw error;
    }
  }

  /**
   * Process appointment cancelled event with transaction handling
   */
  async sendCancellation(appointment) {
    const session = await mongoose.startSession();
    
    try {
      session.startTransaction();
      
      console.log(`[Notification] Starting transaction for cancellation: ${appointment.id}`);
      
      const notification = {
        id: `notif-${Date.now()}`,
        type: 'SMS',
        recipient: appointment.patientId,
        message: `Votre rendez-vous du ${new Date(appointment.dateTime).toLocaleString()} a été annulé.`,
        status: 'PENDING',
        createdAt: new Date()
      };

      // Save notification
      notificationStore.set(notification.id, notification);
      
      // Simulate sending SMS
      notification.status = 'SENT';
      notificationStore.set(notification.id, notification);
      
      // Commit transaction
      await session.commitTransaction();
      session.endSession();
      
      console.log(`[Notification] Transaction committed: SMS sent to ${appointment.patientId}`);
      return notification;
      
    } catch (error) {
      await session.abortTransaction();
      session.endSession();
      console.error(`[Notification] Transaction failed:`, error.message);
      throw error;
    }
  }

  /**
   * Process appointment completed event with transaction handling
   */
  async sendCompletion(appointment) {
    const session = await mongoose.startSession();
    
    try {
      session.startTransaction();
      
      console.log(`[Notification] Starting transaction for completion: ${appointment.id}`);
      
      const notification = {
        id: `notif-${Date.now()}`,
        type: 'EMAIL',
        recipient: appointment.patientId,
        subject: `Compte-rendu de votre visite`,
        message: `Votre consultation s'est terminée. Le compte-rendu est disponible.`,
        status: 'PENDING',
        createdAt: new Date()
      };

      // Save notification
      notificationStore.set(notification.id, notification);
      
      // Simulate sending email
      notification.status = 'SENT';
      notificationStore.set(notification.id, notification);
      
      // Commit transaction
      await session.commitTransaction();
      session.endSession();
      
      console.log(`[Notification] Transaction committed: Completion email sent to ${appointment.patientId}`);
      return notification;
      
    } catch (error) {
      await session.abortTransaction();
      session.endSession();
      console.error(`[Notification] Transaction failed:`, error.message);
      throw error;
    }
  }

  /**
   * Get notification by ID
   */
  async getById(id) {
    return notificationStore.get(id) || null;
  }

  /**
   * Create a new notification manually
   */
  async create(type, recipient, subject, message) {
    const notification = {
      id: `notif-${Date.now()}`,
      type,
      recipient,
      subject: subject || '',
      message,
      status: 'PENDING',
      createdAt: new Date()
    };

    notificationStore.set(notification.id, notification);
    return notification;
  }
}

module.exports = new NotificationService();
