import { Component, OnInit, OnDestroy } from '@angular/core';
import { Observable, combineLatest } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';
import { interval, Subject, BehaviorSubject } from 'rxjs';
import {
  Portfolio,
  PortfolioStock,
  PerformanceMetrics
} from '../../../shared/models/portfolio.model';
import {
  Transaction,
  TransactionSummary
} from '../../../shared/models/transaction.model';
import {
  Stock,
  StockPrice
} from '../../../shared/models/stock.model';
import { User } from '../../../shared/models/user.model';
import { PortfolioService } from '../../../shared/services/portfolio.service';
import { AuthService } from '../../../shared/services/auth.service';
import { PriceService } from '../../../shared/services/price.service';
import { SPX500Service, ComparisonResult } from '../../../shared/services/spx500.service';

interface DashboardSummary {
  totalInvested: number;
  currentValue: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  bestPerformers: PortfolioStock[];
  worstPerformers: PortfolioStock[];
  stocksCount: number;
  availableBudget: number;
  riskLevel: string;
  diversificationScore: number;
  marketComparison?: ComparisonResult;
}

interface ChartDataPoint {
  date: Date;
  value: number;
}

import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NgApexchartsModule } from 'ng-apexcharts';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexStroke,
  ApexDataLabels,
  ApexMarkers,
  ApexYAxis,
  ApexGrid,
  ApexTitleSubtitle,
  ApexFill,
  ApexTooltip,
  ApexTheme
} from 'ng-apexcharts';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  stroke: ApexStroke;
  dataLabels: ApexDataLabels;
  markers: ApexMarkers;
  colors: string[];
  yaxis: ApexYAxis;
  grid: ApexGrid;
  fill: ApexFill;
  tooltip: ApexTooltip;
  theme: ApexTheme;
  title: ApexTitleSubtitle;
};

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, NgApexchartsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Données principales
  portfolio$!: Observable<Portfolio | null>;
  transactions$!: Observable<Transaction[]>;
  user$!: Observable<User | null>;
  transactionSummary$!: Observable<TransactionSummary>;

  // Données dérivées
  dashboardSummary$!: Observable<DashboardSummary>;
  chartData$!: Observable<ChartDataPoint[]>;

  // Configuration du graphique
  public chartOptions: any = {};
  public selectedPeriod$ = new BehaviorSubject<string>('30J');
  public selectedPeriod = '30J'; // Pour l'affichage template facile

  // État de l'interface
  isLoading = true;
  error: string | null = null;

  constructor(
    private portfolioService: PortfolioService,
    private authService: AuthService,
    private priceService: PriceService,
    private spx500Service: SPX500Service
  ) {
    this.initializeChartOptions();
    this.initializeObservables();
  }

  private initializeChartOptions(): void {
    this.chartOptions = {
      series: [{
        name: "Valeur du Portefeuille",
        data: []
      }],
      chart: {
        height: 350,
        type: "area",
        fontFamily: "'Inter', sans-serif",
        background: 'transparent',
        toolbar: {
          show: false
        },
        animations: {
          enabled: true
        },
        zoom: {
          enabled: false
        }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: "smooth",
        width: 2
      },
      xaxis: {
        type: 'datetime',
        labels: {
          style: {
            colors: '#888',
            fontSize: '12px'
          },
          datetimeFormatter: {
            year: 'yyyy',
            month: "MMM",
            day: 'dd MMM',
            hour: 'HH:mm'
          }
        },
        axisBorder: { show: false },
        axisTicks: { show: false },
        tooltip: { enabled: false }
      },
      yaxis: {
        labels: {
          style: {
            colors: '#888',
            fontSize: '12px'
          },
          formatter: (value: number) => {
            return new Intl.NumberFormat('fr-FR', {
              style: 'currency',
              currency: 'EUR',
              maximumFractionDigits: 0
            }).format(value);
          }
        }
      },
      grid: {
        borderColor: 'rgba(255, 255, 255, 0.05)',
        strokeDashArray: 4,
        yaxis: {
          lines: { show: true }
        },
        xaxis: {
          lines: { show: false }
        },
        padding: {
          top: 0,
          right: 0,
          bottom: 0,
          left: 10 // Penser à l'alignement
        }
      },
      colors: ['#3b82f6'], // Bleu Primaire
      fill: {
        type: "gradient",
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.45,
          opacityTo: 0.05,
          stops: [0, 100]
        }
      },
      theme: {
        mode: 'dark' // Sera dynamique idéalement
      },
      tooltip: {
        theme: 'dark',
        x: {
          format: 'dd MMM yyyy'
        },
        y: {
          formatter: function (val: number) {
            return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val);
          }
        }
      }
    };
  }

  private initializeObservables(): void {
    // Observables de base
    this.portfolio$ = this.portfolioService.portfolio$;
    this.transactions$ = this.portfolioService.transactions$;
    this.user$ = this.authService.currentUser$;
    this.transactionSummary$ = this.portfolioService.getTransactionSummary();

    // Observable principal pour le dashboard
    this.dashboardSummary$ = combineLatest([
      this.portfolio$,
      this.user$,
      this.transactionSummary$
    ]).pipe(
      map(([portfolio, user, summary]) => this.calculateDashboardSummary(portfolio, user, summary))
    );

    // Données pour le graphique d'évolution
    this.chartData$ = this.generateChartData();

    // Subscribe to period changes to update local state for template
    this.selectedPeriod$.pipe(takeUntil(this.destroy$)).subscribe(period => {
      this.selectedPeriod = period;
    });
  }

  private calculateDashboardSummary(
    portfolio: Portfolio | null,
    user: User | null,
    summary: TransactionSummary
  ): DashboardSummary {
    if (!portfolio || !user) {
      return {
        totalInvested: 0,
        currentValue: 0,
        totalGainLoss: 0,
        totalGainLossPercent: 0,
        bestPerformers: [],
        worstPerformers: [],
        stocksCount: 0,
        availableBudget: 0,
        riskLevel: 'LOW',
        diversificationScore: 0
      };
    }

    const { stocks } = portfolio;
    const bestPerformers = [...stocks]
      .filter(stock => stock.totalGainLossPercent > 0)
      .sort((a, b) => b.totalGainLossPercent - a.totalGainLossPercent)
      .slice(0, 3);

    const worstPerformers = [...stocks]
      .sort((a, b) => a.totalGainLossPercent - b.totalGainLossPercent)
      .slice(0, 3);

    return {
      totalInvested: portfolio.totalInvested,
      currentValue: portfolio.totalValue,
      totalGainLoss: portfolio.totalGainLoss,
      totalGainLossPercent: portfolio.totalGainLossPercent,
      bestPerformers,
      worstPerformers,
      stocksCount: stocks.length,
      availableBudget: user.currentBudget,
      riskLevel: portfolio.performanceMetrics.riskLevel,
      diversificationScore: portfolio.performanceMetrics.diversificationScore,
      marketComparison: this.spx500Service.compareWithPortfolio(portfolio.performanceMetrics.totalReturn)
    };
  }

  private generateChartData(): Observable<ChartDataPoint[]> {
    return combineLatest([
      this.portfolio$,
      this.transactions$,
      this.selectedPeriod$,
      this.user$
    ]).pipe(
      map(([portfolio, transactions, period, user]) => {
        if (!portfolio || !user) {
          return [];
        }

        // Détermine la durée en jours selon la période selectionnée
        let daysHistory = 30;
        switch (period) {
          case '3M': daysHistory = 90; break;
          case '1A': daysHistory = 365; break;
          default: daysHistory = 30;
        }

        const chartData: ChartDataPoint[] = [];
        const today = new Date();
        // Normaliser today à minuit pour les comparaisons de date cohérentes
        today.setHours(0, 0, 0, 0);

        const startDate = new Date(today);
        startDate.setDate(today.getDate() - daysHistory);

        // Simulation de l'évolution
        // On part du principe: Valeur Totale = Cash + Valeur Investie

        let currentCash = user.initialBudget;
        let currentInvested = 0;

        // Trie les transactions par date
        const sortedTransactions = [...transactions].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        // 1. Appliquer toutes les transactions antérieures à startDate pour avoir l'état initial
        sortedTransactions.forEach(t => {
          const tDate = new Date(t.date);
          tDate.setHours(0, 0, 0, 0);

          if (tDate < startDate) {
            if (t.type === 'BUY') {
              currentCash -= t.totalAmount;
              currentInvested += t.totalAmount;
            } else {
              currentCash += t.totalAmount;
              currentInvested -= t.totalAmount;
            }
          }
        });

        // S'assurer que les valeurs sont cohérentes (pas de négatif dû à des approximations)
        currentInvested = Math.max(0, currentInvested);

        // 2. Générer les points jour par jour de startDate à today
        for (let i = 0; i <= daysHistory; i++) {
          const currentDate = new Date(startDate);
          currentDate.setDate(startDate.getDate() + i);

          // Appliquer les transactions de CE jour
          const txOfTheDay = sortedTransactions.filter(t => {
            const tDate = new Date(t.date);
            tDate.setHours(0, 0, 0, 0);
            return tDate.getTime() === currentDate.getTime();
          });

          txOfTheDay.forEach(t => {
            if (t.type === 'BUY') {
              currentCash -= t.totalAmount;
              currentInvested += t.totalAmount;
            } else {
              currentCash += t.totalAmount;
              currentInvested -= t.totalAmount;
            }
          });

          // Variation aléatoire quotidienne UNIQUEMENT sur la partie investie
          // (Le cash ne bouge pas avec le marché)
          if (currentInvested > 0) {
            const variation = (Math.random() - 0.5) * 0.02; // ±1%
            currentInvested = currentInvested * (1 + variation);
          }

          // Total Portefeuille = Cash + Investi
          chartData.push({
            date: new Date(currentDate), // Copie la date
            value: Math.round(currentCash + currentInvested)
          });
        }

        // 3. Ajustement final pour coller à la réalité d'aujourd'hui
        // La dernière valeur doit correspondre à (Budget Actuel + Valeur Portefeuille Actuelle)
        if (chartData.length > 0) {
          const actualTotalValue = user.currentBudget + portfolio.totalValue;
          // Lissage exponentiel pour éviter un saut brutal sur le dernier point si la simulation a dévié
          const lastSimulated = chartData[chartData.length - 1].value;

          // Si l'écart est trop grand, on pourrait relisser les derniers jours, 
          // mais pour l'instant on force juste le dernier point pour être exact à l'instant T
          chartData[chartData.length - 1].value = actualTotalValue;
        }

        return chartData;
      })
    );
  }

  setPeriod(period: string): void {
    this.selectedPeriod$.next(period);
  }

  ngOnInit(): void {
    // Met à jour les données du graphique
    this.chartData$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => {
      if (data && data.length > 0) {
        this.chartOptions.series = [{
          name: "Valeur du Portefeuille",
          data: data.map(point => [point.date.getTime(), point.value])
        }];
      }
    });

    this.dashboardSummary$.pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (summary) => {
        this.isLoading = false;
        this.error = null;
      },
      error: (error) => {
        this.isLoading = false;
        this.error = 'Erreur lors du chargement des données du dashboard';
        console.error('Dashboard error:', error);
      }
    });

    // Actualisation automatique des prix toutes les 10 secondes
    interval(10000).pipe(
      takeUntil(this.destroy$)
    ).subscribe(() => {
      this.refreshPrices();
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
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

  getPerformanceClass(value: number): string {
    if (value > 0) return 'text-success';
    if (value < 0) return 'text-danger';
    return 'text-secondary';
  }

  getRiskLevelClass(level: string): string {
    switch (level) {
      case 'LOW': return 'badge-success';
      case 'MEDIUM': return 'badge-warning';
      case 'HIGH': return 'badge-danger';
      case 'VERY_HIGH': return 'badge-danger';
      default: return 'badge-secondary';
    }
  }

  getRiskLevelLabel(level: string): string {
    switch (level) {
      case 'LOW': return 'FAIBLE';
      case 'MEDIUM': return 'MOYEN';
      case 'HIGH': return 'ÉLEVÉ';
      case 'VERY_HIGH': return 'TRÈS ÉLEVÉ';
      default: return 'INCONNU';
    }
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

  exportData(): void {
    const exportData = this.portfolioService.exportHistory();
    const blob = new Blob([exportData], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `portfolio-export-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    window.URL.revokeObjectURL(url);
  }
}
