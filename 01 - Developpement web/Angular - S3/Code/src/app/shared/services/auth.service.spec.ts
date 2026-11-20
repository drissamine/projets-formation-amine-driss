import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { User } from '../models/user.model';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthService);

    // Nettoie le localStorage avant chaque test
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should login with valid credentials', (done) => {
      const credentials = { email: 'test@example.com', password: 'password123' };

      service.login(credentials).subscribe(result => {
        expect(result).toBe(true);
        expect(service.currentUser).toBeTruthy();
        expect(service.currentUser?.email).toBe(credentials.email);
        done();
      });
    });

    it('should fail login with invalid credentials', (done) => {
      const credentials = { email: '', password: '' };

      service.login(credentials).subscribe(result => {
        expect(result).toBe(false);
        expect(service.currentUser).toBeFalsy();
        done();
      });
    });

    it('should update budget after successful login', (done) => {
      const credentials = { email: 'test@example.com', password: 'password123' };

      service.login(credentials).subscribe(result => {
        expect(result).toBe(true);
        expect(service.currentUser?.currentBudget).toBe(10000);
        done();
      });
    });
  });

  describe('logout', () => {
    it('should clear user and emit null', (done) => {
      // Login d'abord
      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe(() => {
        expect(service.currentUser).toBeTruthy();

        service.logout();

        expect(service.currentUser).toBeFalsy();
        done();
      });
    });
  });

  describe('updateBudget', () => {
    it('should update user budget', (done) => {
      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe(() => {
        const newBudget = 5000;
        service.updateBudget(newBudget);

        expect(service.currentUser?.currentBudget).toBe(newBudget);
        done();
      });
    });

    it('should not update budget when not logged in', () => {
      service.updateBudget(5000);
      expect(service.currentUser).toBeFalsy();
    });
  });

  describe('register', () => {
    it('should register new user successfully', (done) => {
      const profile = {
        name: 'Test User',
        email: 'newuser@example.com',
        initialBudget: 5000
      };

      service.register(profile).subscribe(result => {
        expect(result).toBe(true);
        expect(service.currentUser).toBeTruthy();
        expect(service.currentUser?.email).toBe(profile.email);
        expect(service.currentUser?.name).toBe(profile.name);
        expect(service.currentUser?.currentBudget).toBe(profile.initialBudget);
        done();
      });
    });

    it('should fail registration with invalid data', (done) => {
      const profile = {
        name: '',
        email: '',
        initialBudget: 0
      };

      service.register(profile).subscribe(result => {
        expect(result).toBe(false);
        done();
      });
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when user is logged in', (done) => {
      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe(() => {
        expect(service.isAuthenticated).toBe(true);
        done();
      });
    });

    it('should return false when user is not logged in', () => {
      expect(service.isAuthenticated).toBe(false);
    });
  });

  describe('currentUser$', () => {
    it('should emit user after successful login', (done) => {
      service.currentUser$.subscribe(user => {
        if (user) {
          expect(user.email).toBe('test@example.com');
          done();
        }
      });

      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe();
    });

    it('should emit null after logout', (done) => {
      let emissionCount = 0;

      service.currentUser$.subscribe(user => {
        emissionCount++;

        if (emissionCount === 1) {
          // Première emission (initiale) : null
          expect(user).toBeNull();
        } else if (emissionCount === 2) {
          // Deuxième emission : après login
          expect(user).toBeTruthy();
          // Appel de logout de manière asynchrone pour éviter la récursion synchrone si tout est synchrone
          setTimeout(() => service.logout());
        } else if (emissionCount === 3) {
          // Troisième emission : après logout
          expect(user).toBeFalsy();
          done();
        }
      });

      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe();
    });
  });

  describe('updateProfile', () => {
    it('should update user profile', (done) => {
      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe(() => {
        const profileUpdates = {
          name: 'Updated User'
        };

        service.updateProfile(profileUpdates);

        expect(service.currentUser?.name).toBe('Updated User');
        done();
      });
    });
  });

  describe('localStorage persistence', () => {
    it('should persist user data in localStorage', (done) => {
      const credentials = { email: 'test@example.com', password: 'password123' };
      service.login(credentials).subscribe(() => {
        // Vérifie que les données sont sauvegardées
        const storedUser = localStorage.getItem('stock_portfolio_user');
        expect(storedUser).toBeTruthy();
        done();
      });
    });

    it('should restore user from localStorage on service creation', () => {
      // Simule un utilisateur déjà connecté
      const mockUser: User = {
        id: 'test-id',
        email: 'test@example.com',
        name: 'Test User',
        currentBudget: 5000,
        initialBudget: 10000,
        isAuthenticated: true,
        createdAt: new Date()
      };

      localStorage.setItem('stock_portfolio_user', JSON.stringify(mockUser));

      // Crée une nouvelle instance du service
      const newService = new AuthService();

      expect(newService.currentUser).toBeTruthy();
      expect(newService.currentUser?.email).toBe(mockUser.email);
    });

    it('should handle corrupted localStorage data', () => {
      // Simule des données corrompues
      localStorage.setItem('stock_portfolio_user', 'invalid-json');

      // Espionne console.error pour éviter de polluer la sortie des tests
      spyOn(console, 'error');

      // Crée une nouvelle instance du service
      const newService = new AuthService();

      expect(newService.currentUser).toBeFalsy();
      expect(console.error).toHaveBeenCalled();
    });
  });
});
