import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { PerformanceService } from '../../../shared/services/performance.service';
import { AuthService } from '../../../shared/services/auth.service';
// PrimeNG imports
import { CardModule } from 'primeng/card';

@Component({
  selector: 'app-portfolio-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    CardModule
  ],
  templateUrl: './portfolio-dashboard.html',
  styleUrl: './portfolio-dashboard.scss'
})
export class PortfolioDashboardComponent implements OnInit {
  totalValue$: Observable<number>;
  balance: number = 0;

  constructor(
    private performanceService: PerformanceService,
    private authService: AuthService
  ) {
    this.totalValue$ = this.performanceService.getTotalValue();
  }

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.balance = user.currentBudget;
      }
    });
  }
}
