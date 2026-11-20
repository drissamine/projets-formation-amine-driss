import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { User, LoginCredentials, UserProfile } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly STORAGE_KEY = 'stock_portfolio_user';
  private currentUserSubject = new BehaviorSubject<User | null>(this.getUserFromStorage());
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor() { }

  /**
   * Vérifie si l'utilisateur est connecté
   */
  get isAuthenticated(): boolean {
    return this.currentUserSubject.value?.isAuthenticated ?? false;
  }

  /**
   * Retourne l'utilisateur courant
   */
  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Connexion utilisateur
   */
  login(credentials: LoginCredentials): Observable<boolean> {
    return new Observable(observer => {
      // Simulation d'une authentification simple
      if (credentials.email && credentials.password) {
        const user: User = {
          id: this.generateId(),
          name: this.extractNameFromEmail(credentials.email),
          email: credentials.email,
          initialBudget: 10000, // Budget initial par défaut
          currentBudget: 10000,
          isAuthenticated: true,
          createdAt: new Date()
        };

        this.saveUserToStorage(user);
        this.currentUserSubject.next(user);
        observer.next(true);
        observer.complete();
      } else {
        observer.next(false);
        observer.complete();
      }
    });
  }

  /**
   * Inscription utilisateur
   */
  register(profile: UserProfile): Observable<boolean> {
    return new Observable(observer => {
      if (profile.name && profile.email && profile.initialBudget > 0) {
        const user: User = {
          id: this.generateId(),
          name: profile.name,
          email: profile.email,
          initialBudget: profile.initialBudget,
          currentBudget: profile.initialBudget,
          isAuthenticated: true,
          createdAt: new Date()
        };

        this.saveUserToStorage(user);
        this.currentUserSubject.next(user);
        observer.next(true);
        observer.complete();
      } else {
        observer.next(false);
        observer.complete();
      }
    });
  }

  /**
   * Déconnexion
   */
  logout(): void {
    localStorage.removeItem(this.STORAGE_KEY);
    this.currentUserSubject.next(null);
  }

  /**
   * Met à jour le profil utilisateur
   */
  updateProfile(profile: Partial<UserProfile>): void {
    const currentUser = this.currentUserSubject.value;
    if (currentUser) {
      const updatedUser: User = {
        ...currentUser,
        ...profile
      };

      this.saveUserToStorage(updatedUser);
      this.currentUserSubject.next(updatedUser);
    }
  }

  /**
   * Met à jour le budget disponible
   */
  updateBudget(newBudget: number): void {
    const currentUser = this.currentUserSubject.value;
    if (currentUser) {
      const updatedUser: User = {
        ...currentUser,
        currentBudget: newBudget
      };

      this.saveUserToStorage(updatedUser);
      this.currentUserSubject.next(updatedUser);
    }
  }

  /**
   * Sauvegarde l'utilisateur dans le localStorage
   */
  private saveUserToStorage(user: User): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(user));
  }

  /**
   * Récupère l'utilisateur du localStorage
   */
  private getUserFromStorage(): User | null {
    const userJson = localStorage.getItem(this.STORAGE_KEY);
    if (userJson) {
      try {
        const user = JSON.parse(userJson);
        user.createdAt = new Date(user.createdAt);
        return user;
      } catch (error) {
        console.error('Erreur lors de la désérialisation de l\'utilisateur:', error);
        return null;
      }
    }
    return null;
  }

  /**
   * Génère un ID unique
   */
  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Extrait le nom depuis l'email
   */
  private extractNameFromEmail(email: string): string {
    return email.split('@')[0];
  }
}
