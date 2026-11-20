export class User {
  constructor({ id, email, password, name, role, createdAt }) {
    this.id = id;
    this.email = email;
    this.password = password;
    this.name = name;
    this.role = role || 'CUSTOMER';
    this.createdAt = createdAt;
  }

  static create({ email, password, name, role }) {
    // Validation logic could go here
    return new User({
        email,
        password,
        name,
        role
    });
  }
}
