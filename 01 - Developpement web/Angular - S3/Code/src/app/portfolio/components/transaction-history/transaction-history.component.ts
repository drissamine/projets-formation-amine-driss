import { Component, OnInit, OnDestroy } from '@angular/core';
import { Observable } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';
import { Transaction } from '../../../shared/models/transaction.model';
import { PortfolioService } from '../../../shared/services/portfolio.service';

import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-transaction-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './transaction-history.component.html',
  styleUrls: ['./transaction-history.component.scss']
})
export class TransactionHistoryComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  transactions$: Observable<Transaction[]>;
  isLoading = true;
  error: string | null = null;

  constructor(private portfolioService: PortfolioService) {
    this.transactions$ = this.portfolioService.transactions$.pipe(
      map(transactions => [...transactions].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()))
    );
  }

  ngOnInit(): void {
    this.transactions$.pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (data) => {
        console.log('TransactionHistory received:', data);
        this.isLoading = false;
      },
      error: (error) => {
        this.isLoading = false;
        this.error = 'Erreur lors du chargement de l\'historique';
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }

  formatDate(date: Date): string {
    return new Intl.DateTimeFormat('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }
}
