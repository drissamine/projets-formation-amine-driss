/**
 * Appointment Aggregate
 * Represents a scheduled appointment in the MediCare system
 */
class Appointment {
  constructor(id, patientId, doctorId, dateTime, specialty) {
    this.id = id;
    this.patientId = patientId;
    this.doctorId = doctorId;
    this.dateTime = new Date(dateTime);
    this.specialty = specialty;
    this.status = 'SCHEDULED';
    this.domainEvents = [];
  }

  /**
   * Invariant: Can only cancel scheduled appointments
   * @throws Error if appointment is not in SCHEDULED status
   */
  cancel() {
    if (this.status !== 'SCHEDULED') {
      throw new Error('Cannot cancel appointment: status must be SCHEDULED');
    }
    this.status = 'CANCELLED';
    this.addDomainEvent({
      type: 'AppointmentCancelled',
      data: {
        appointmentId: this.id,
        patientId: this.patientId,
        doctorId: this.doctorId,
        dateTime: this.dateTime
      }
    });
  }

  /**
   * Invariant: Can only complete scheduled appointments
   * @throws Error if appointment is not in SCHEDULED status
   */
  complete() {
    if (this.status !== 'SCHEDULED') {
      throw new Error('Cannot complete appointment: status must be SCHEDULED');
    }
    this.status = 'COMPLETED';
    this.addDomainEvent({
      type: 'AppointmentCompleted',
      data: { 
        appointmentId: this.id, 
        patientId: this.patientId 
      }
    });
  }

  addDomainEvent(event) {
    this.domainEvents.push(event);
  }

  clearDomainEvents() {
    this.domainEvents = [];
  }

  toJSON() {
    return {
      id: this.id,
      patientId: this.patientId,
      doctorId: this.doctorId,
      dateTime: this.dateTime,
      specialty: this.specialty,
      status: this.status
    };
  }
}

module.exports = Appointment;
