import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { PerformanceService } from './performance.service';
import { PortfolioService } from './portfolio.service';
import { PriceService } from './price.service';
import { AuthService } from './auth.service';


describe('PerformanceService', () => {
  let service: PerformanceService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      providers: [PortfolioService, PriceService, AuthService]
    });
    service = TestBed.inject(PerformanceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
