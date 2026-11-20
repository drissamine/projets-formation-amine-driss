import { TestBed } from '@angular/core/testing';
import { AlertService } from './alert.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AlertType, PortfolioAlert } from '../models/portfolio.model';
import { of, BehaviorSubject } from 'rxjs';
import { AuthService } from './auth.service';
import { PortfolioService } from './portfolio.service';
import { PriceService } from './price.service';

describe('AlertService', () => {
  let service: AlertService;
  let mockAuthService: any;
  let mockPortfolioService: any;
  let mockPriceService: any;

  beforeEach(() => {
    const store: { [key: string]: string } = {};

    const mockLocalStorage = {
      getItem: (key: string): string | null => {
        return key in store ? store[key] : null;
      },
      setItem: (key: string, value: string) => {
        store[key] = `${value}`;
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        for (const key in store) {
          delete store[key];
        }
      }
    };

    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true
    });

    mockAuthService = {
      currentUser$: of({ id: 'test-user', isAuthenticated: true }),
      get currentUser() { return { id: 'test-user', isAuthenticated: true }; }
    };

    mockPortfolioService = {
      portfolioSubject: new BehaviorSubject(null)
    };

    mockPriceService = {
      getAllStockPrices: () => of({}),
      stockPrices: new BehaviorSubject({})
    };

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AlertService,
        { provide: AuthService, useValue: mockAuthService },
        { provide: PortfolioService, useValue: mockPortfolioService },
        { provide: PriceService, useValue: mockPriceService }
      ]
    });
    service = TestBed.inject(AlertService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should add alert successfully', (done) => {
    service.createAlert('AAPL', AlertType.PRICE_RISE, 200).subscribe(success => {
      expect(success).toBeTrue();
      service.alerts$.subscribe(alerts => {
        const alert = alerts.find(a => a.stockSymbol === 'AAPL');
        expect(alert).toBeTruthy();
        expect(alert?.stockSymbol).toBe('AAPL');
        expect(alert?.alertType).toBe(AlertType.PRICE_RISE);
        expect(alert?.threshold).toBe(200);
        expect(alert?.isTriggered).toBe(false);
        done();
      });
    });
  });

  it('should remove alert successfully', (done) => {
    service.createAlert('GOOG', AlertType.PRICE_DROP, 100).subscribe(() => {
      service.alerts$.subscribe(alerts => {
        const alert = alerts.find(a => a.stockSymbol === 'GOOG');
        if (alert) {
          service.deleteAlert(alert.id);
          service.alerts$.subscribe(updatedAlerts => {
            const foundAlert = updatedAlerts.find(a => a.id === alert.id);
            expect(foundAlert).toBeUndefined();
            done();
          });
        }
      });
    });
  });

  it('should get alerts by symbol', (done) => {
    service.createAlert('AAPL', AlertType.PRICE_RISE, 200).subscribe(() => {
      service.createAlert('AAPL', AlertType.PRICE_DROP, 150).subscribe(() => {
        service.createAlert('GOOG', AlertType.PRICE_RISE, 100).subscribe(() => {
          service.getAlertsForSymbol('AAPL').subscribe(aaplAlerts => {
            expect(aaplAlerts.length).toBe(2);
            service.getAlertsForSymbol('GOOG').subscribe(googAlerts => {
              expect(googAlerts.length).toBe(1);
              done();
            });
          });
        });
      });
    });
  });
});
