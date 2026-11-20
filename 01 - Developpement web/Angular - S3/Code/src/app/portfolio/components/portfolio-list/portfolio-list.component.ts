import { Component, OnInit, OnDestroy } from '@angular/core';
import { Observable, combineLatest } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';
import {
  Portfolio,
  PortfolioStock
} from '../../../shared/models/portfolio.model';
import { Stock, StockPrice } from '../../../shared/models/stock.model';
import { User } from '../../../shared/models/user.model';
import { PortfolioService } from '../../../shared/services/portfolio.service';
import { AuthService } from '../../../shared/services/auth.service';
import { PriceService } from '../../../shared/services/price.service';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-portfolio-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './portfolio-list.component.html',
  styleUrls: ['./portfolio-list.component.scss']
})
export class PortfolioListComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Données principales
  portfolio$!: Observable<Portfolio | null>;
  user$!: Observable<User | null>;
  stocks$!: Observable<PortfolioStock[]>;

  // État de l'interface
  isLoading = true;
  error: string | null = null;
  sortColumn: string = 'symbol';
  sortDirection: 'asc' | 'desc' = 'asc';
  filterSymbol: string = '';

  constructor(
    private portfolioService: PortfolioService,
    private authService: AuthService,
    private priceService: PriceService
  ) {
    this.initializeObservables();
  }

  private initializeObservables(): void {
    this.portfolio$ = this.portfolioService.portfolio$;
    this.user$ = this.authService.currentUser$;

    // Observable pour les actions avec tri et filtrage
    this.stocks$ = combineLatest([
      this.portfolio$,
      this.user$
    ]).pipe(
      map(([portfolio, user]) => {
        if (!portfolio || !user || portfolio.stocks.length === 0) {
          return [];
        }

        let stocks = [...portfolio.stocks];

        // Filtrage par symbole
        if (this.filterSymbol) {
          stocks = stocks.filter(stock =>
            stock.symbol.toLowerCase().includes(this.filterSymbol.toLowerCase())
          );
        }

        // Tri
        stocks.sort((a, b) => {
          let aValue: any = a[this.sortColumn as keyof PortfolioStock];
          let bValue: any = b[this.sortColumn as keyof PortfolioStock];

          if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase();
            bValue = (bValue as string).toLowerCase();
          }

          if (this.sortDirection === 'asc') {
            return aValue > bValue ? 1 : -1;
          } else {
            return aValue < bValue ? 1 : -1;
          }
        });

        return stocks;
      })
    );
  }

  ngOnInit(): void {
    this.stocks$.pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (stocks) => {
        this.isLoading = false;
        this.error = null;
      },
      error: (error) => {
        this.isLoading = false;
        this.error = 'Erreur lors du chargement du portefeuille';
        console.error('Portfolio list error:', error);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // Gestion du tri
  sort(column: string): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
  }

  getSortIcon(column: string): string {
    if (this.sortColumn !== column) {
      return 'fas fa-sort';
    }
    return this.sortDirection === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
  }

  // Gestion du filtrage
  onFilterChange(): void {
    this.initializeObservables(); // Re-initialise pour appliquer le filtre
  }

  clearFilter(): void {
    this.filterSymbol = '';
    this.initializeObservables();
  }

  // Utilitaires pour l'affichage
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }

  formatPercentage(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100);
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

  // Classes CSS conditionnelles
  getPerformanceClass(value: number): string {
    if (value > 0) return 'text-success';
    if (value < 0) return 'text-danger';
    return 'text-secondary';
  }

  getChangeClass(value: number): string {
    if (value > 0) return 'text-success';
    if (value < 0) return 'text-danger';
    return 'text-secondary';
  }

  // Actions
  refreshPrices(): void {
    this.priceService.refreshPrices().subscribe({
      next: () => {
        // Les prix sont automatiquement mis à jour via les BehaviorSubjects
      },
      error: (error) => {
        console.error('Erreur lors de la mise à jour des prix:', error);
      }
    });
  }

  sellStock(symbol: string): void {
    // Redirige vers la page de vente avec le symbole pré-sélectionné
    // Nous implémenterons cela plus tard
    console.log(`Vendre des actions ${symbol}`);
  }

  viewDetails(symbol: string): void {
    // Affiche les détails d'une action
    // Nous implémenterons cela plus tard
    console.log(`Voir détails de ${symbol}`);
  }
}
