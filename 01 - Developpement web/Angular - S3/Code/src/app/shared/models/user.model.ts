export interface User {
  id: string;
  name: string;
  email: string;
  initialBudget: number;
  currentBudget: number;
  isAuthenticated: boolean;
  createdAt: Date;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface UserProfile {
  name: string;
  email: string;
  initialBudget: number;
}
