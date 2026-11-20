import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, combineLatest } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import {
  Portfolio,
  PortfolioStock,
  PerformanceMetrics,
  RiskLevel,
  AssetAllocation,
  PortfolioComparison,
  PortfolioAlert,
  AlertType,
  PortfolioEvent,
  PortfolioEventType
} from '../models/portfolio.model';
import {
  Transaction,
  TransactionType,
  TransactionSummary
} from '../models/transaction.model';
import { StockPrice } from '../models/stock.model';
import { AuthService } from './auth.service';
import { PriceService } from './price.service';

@Injectable({
  providedIn: 'root'
})
export class PortfolioService {
  private readonly STORAGE_KEY = 'stock_portfolio_transactions';

  // État du portefeuille
  private portfolioSubject = new BehaviorSubject<Portfolio | null>(null);
  public portfolio$ = this.portfolioSubject.asObservable();

  // État des transactions
  private transactionsSubject = new BehaviorSubject<Transaction[]>([]);
  public transactions$ = this.transactionsSubject.asObservable();

  // État des alerts
  private alertsSubject = new BehaviorSubject<PortfolioAlert[]>([]);
  public alerts$ = this.alertsSubject.asObservable();

  // Événements du portefeuille
  private eventsSubject = new BehaviorSubject<PortfolioEvent | null>(null);
  public events$ = this.eventsSubject.asObservable();

  constructor(
    private authService: AuthService,
    private priceService: PriceService
  ) {
    // Charge les données au démarrage
    this.loadUserData();

    // Écoute les changements d'utilisateur
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        // Ne recharger que si l'utilisateur a changé (évite le rechargement lors de la mise à jour du budget)
        if (this.currentUserId !== user.id) {
          this.currentUserId = user.id;
          this.loadUserData();
        }
      } else {
        this.currentUserId = null;
        this.clearUserData();
      }
    });

    // Met à jour le portefeuille quand les prix changent
    this.priceService.getAllStockPrices().subscribe(() => {
      this.updatePortfolio();
    });
  }

  private currentUserId: string | null = null;

  /**
   * Charge les données utilisateur depuis le localStorage
   */
  private loadUserData(): void {
    const user = this.authService.currentUser;
    if (!user) return;

    const transactionsJson = localStorage.getItem(`${this.STORAGE_KEY}_${user.id}`);
    const alertsJson = localStorage.getItem(`portfolio_alerts_${user.id}`);

    const transactions: Transaction[] = transactionsJson
      ? JSON.parse(transactionsJson).map((t: any) => ({
        ...t,
        date: new Date(t.date)
      }))
      : [];

    const alerts: PortfolioAlert[] = alertsJson
      ? JSON.parse(alertsJson).map((a: any) => ({
        ...a,
        createdAt: new Date(a.createdAt),
        triggeredAt: a.triggeredAt ? new Date(a.triggeredAt) : undefined
      }))
      : [];

    this.transactionsSubject.next(transactions);
    this.alertsSubject.next(alerts);
    this.updatePortfolio();
  }

  /**
   * Sauvegarde les transactions utilisateur
   */
  private saveTransactions(): void {
    const user = this.authService.currentUser;
    if (!user) return;

    localStorage.setItem(
      `${this.STORAGE_KEY}_${user.id}`,
      JSON.stringify(this.transactionsSubject.value)
    );
  }

  /**
   * Sauvegarde les alerts utilisateur
   */
  private saveAlerts(): void {
    const user = this.authService.currentUser;
    if (!user) return;

    localStorage.setItem(
      `portfolio_alerts_${user.id}`,
      JSON.stringify(this.alertsSubject.value)
    );
  }

  /**
   * Met à jour le portefeuille avec les données actuelles
   */
  private updatePortfolio(): void {
    const user = this.authService.currentUser;
    if (!user) return;

    const transactions = this.transactionsSubject.value;

    // Utiliser le Subject public ou une méthode publique pour obtenir la valeur actuelle
    // Idéalement, PriceService devrait exposer une méthode getValue() ou on devrait s'abonner avec take(1)
    let currentPrices: { [key: string]: StockPrice } = {};
    const pricesSubscription = this.priceService.getAllStockPrices().subscribe(prices => {
      currentPrices = prices;
    });
    pricesSubscription.unsubscribe();

    if (transactions.length === 0) {
      this.portfolioSubject.next(this.createEmptyPortfolio(user.id));
      return;
    }

    // Groupe les transactions par symbole
    const stockGroups = this.groupTransactionsByStock(transactions);

    // Calcule les métriques pour chaque action
    const portfolioStocks: PortfolioStock[] = [];
    let totalValue = 0;
    let totalInvested = 0;

    Object.keys(stockGroups).forEach(symbol => {
      const group = stockGroups[symbol];
      const stockPrice = currentPrices[symbol];

      // Si le prix n'est pas disponible, on ignore cette action ou on gère l'erreur
      if (stockPrice) {
        const stockMetrics = this.calculateStockMetrics(group, stockPrice);

        if (stockMetrics.shares > 0) {
          portfolioStocks.push(stockMetrics);
          totalValue += stockMetrics.totalValue;
          totalInvested += stockMetrics.shares * stockMetrics.averageCost;
        }
      } else {
        console.warn(`Prix non disponible pour le symbole: ${symbol}`);
      }
    });

    // Calcule les métriques de performance
    const performanceMetrics = this.calculatePerformanceMetrics(portfolioStocks, totalInvested, totalValue);

    const portfolio: Portfolio = {
      userId: user.id,
      stocks: portfolioStocks,
      totalValue,
      totalInvested,
      totalGainLoss: totalValue - totalInvested,
      totalGainLossPercent: totalInvested > 0 ? ((totalValue - totalInvested) / totalInvested) * 100 : 0,
      performanceMetrics,
      lastUpdated: new Date()
    };

    this.portfolioSubject.next(portfolio);
  }

  /**
   * Crée un portefeuille vide
   */
  private createEmptyPortfolio(userId: string): Portfolio {
    return {
      userId,
      stocks: [],
      totalValue: 0,
      totalInvested: 0,
      totalGainLoss: 0,
      totalGainLossPercent: 0,
      performanceMetrics: {
        totalReturn: 0,
        weightedReturn: 0,
        volatility: 0,
        diversificationScore: 0,
        riskLevel: RiskLevel.LOW
      },
      lastUpdated: new Date()
    };
  }

  /**
   * Groupe les transactions par symbole d'action
   */
  private groupTransactionsByStock(transactions: Transaction[]): { [symbol: string]: Transaction[] } {
    return transactions.reduce((groups, transaction) => {
      const symbol = transaction.stockSymbol;
      if (!groups[symbol]) {
        groups[symbol] = [];
      }
      groups[symbol].push(transaction);
      return groups;
    }, {} as { [symbol: string]: Transaction[] });
  }

  /**
   * Calcule les métriques pour une action
   */
  private calculateStockMetrics(transactions: Transaction[], currentPrice: StockPrice): PortfolioStock {
    let totalShares = 0;
    let totalCost = 0; // Coût de base (Cost Basis)
    let realizedGainLoss = 0;

    // Trier les transactions par date pour assurer la séquence de calcul correcte
    const sortedTransactions = [...transactions].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    sortedTransactions.forEach(transaction => {
      if (transaction.type === TransactionType.BUY) {
        totalShares += transaction.shares;
        totalCost += transaction.totalAmount;
      } else {
        // Lors d'une vente, on réduit le coût total ("Cost Basis") proportionnellement
        // Coût moyen au moment de la vente
        const averageCostAtSale = totalShares > 0 ? totalCost / totalShares : 0;

        // On réduit le coût total de la valeur des actions vendues (au prix moyen d'achat)
        const costOfSoldShares = transaction.shares * averageCostAtSale;
        totalCost -= costOfSoldShares;

        totalShares -= transaction.shares;
        realizedGainLoss += (transaction.realizedGainLoss || 0);
      }
    });

    // Coût moyen actuel
    const averageCost = totalShares > 0 ? totalCost / totalShares : 0;

    const currentValue = totalShares * currentPrice.price;

    // Plus/Moins value latente (Unrealized P&L)
    const totalGainLoss = currentValue - totalCost;

    const totalGainLossPercent = totalCost > 0 ? (totalGainLoss / totalCost) * 100 : 0;

    const totalPortfolioValue = this.portfolioSubject.value?.totalValue || 0;
    const allocationPercent = totalPortfolioValue > 0 ? (currentValue / totalPortfolioValue) * 100 : 0;

    return {
      symbol: currentPrice.symbol,
      shares: totalShares,
      averageCost,
      currentPrice: currentPrice.price,
      totalValue: currentValue,
      totalGainLoss,
      totalGainLossPercent,
      gainLossSincePurchase: totalGainLoss + realizedGainLoss,
      gainLossSincePurchasePercent: (totalCost > 0) ? ((totalGainLoss + realizedGainLoss) / totalCost) * 100 : 0,
      allocationPercent,
      lastUpdated: currentPrice.timestamp
    };
  }

  /**
   * Calcule les métriques de performance du portefeuille
   */
  private calculatePerformanceMetrics(
    stocks: PortfolioStock[],
    totalInvested: number,
    totalValue: number
  ): PerformanceMetrics {
    const totalReturn = totalInvested > 0 ? ((totalValue - totalInvested) / totalInvested) * 100 : 0;

    // Performance pondérée basée sur les allocations
    const weightedReturn = stocks.reduce((sum, stock) => {
      const weight = totalValue > 0 ? stock.totalValue / totalValue : 0;
      return sum + (stock.totalGainLossPercent * weight);
    }, 0);

    // Volatilité simulée (basée sur la variance des rendements)
    const volatility = this.calculateVolatility(stocks);

    // Score de diversification (nombre d'actions différentes)
    const diversificationScore = Math.min(100, (stocks.length / 10) * 100);

    // Niveau de risque basé sur la volatilité et la diversification
    const riskLevel = this.determineRiskLevel(volatility, diversificationScore);

    return {
      totalReturn,
      weightedReturn,
      volatility,
      diversificationScore,
      riskLevel
    };
  }

  /**
   * Calcule la volatilité du portefeuille
   */
  private calculateVolatility(stocks: PortfolioStock[]): number {
    if (stocks.length === 0) return 0;

    const avgReturn = stocks.reduce((sum, stock) => sum + stock.totalGainLossPercent, 0) / stocks.length;
    const variance = stocks.reduce((sum, stock) => {
      const diff = stock.totalGainLossPercent - avgReturn;
      return sum + (diff * diff);
    }, 0) / stocks.length;

    return Math.sqrt(variance);
  }

  /**
   * Détermine le niveau de risque
   */
  private determineRiskLevel(volatility: number, diversificationScore: number): RiskLevel {
    if (volatility > 30 || diversificationScore < 30) return RiskLevel.VERY_HIGH;
    if (volatility > 20 || diversificationScore < 50) return RiskLevel.HIGH;
    if (volatility > 10 || diversificationScore < 70) return RiskLevel.MEDIUM;
    return RiskLevel.LOW;
  }

  /**
   * Achète des actions
   */
  buyStock(symbol: string, shares: number, pricePerShare: number): Observable<boolean> {
    return new Observable(observer => {
      const user = this.authService.currentUser;
      if (!user) {
        observer.next(false);
        observer.complete();
        return;
      }

      const totalCost = shares * pricePerShare;
      if (totalCost > user.currentBudget) {
        observer.next(false);
        observer.complete();
        return;
      }

      const transaction: Transaction = {
        id: this.generateId(),
        userId: user.id,
        stockSymbol: symbol.toUpperCase(),
        type: TransactionType.BUY,
        shares,
        pricePerShare,
        totalAmount: totalCost,
        fees: 0,
        date: new Date()
      };

      const currentTransactions = this.transactionsSubject.value;
      this.transactionsSubject.next([...currentTransactions, transaction]);

      // Met à jour le budget
      this.authService.updateBudget(user.currentBudget - totalCost);

      this.saveTransactions();
      this.updatePortfolio();

      // Émettre l'événement
      this.eventsSubject.next({
        type: PortfolioEventType.BUY,
        stockSymbol: symbol.toUpperCase(),
        quantity: shares,
        price: pricePerShare,
        totalAmount: totalCost,
        timestamp: new Date()
      });

      observer.next(true);
      observer.complete();
    });
  }

  /**
   * Vend des actions
   */
  sellStock(symbol: string, shares: number, pricePerShare: number): Observable<boolean> {
    return new Observable(observer => {
      const user = this.authService.currentUser;
      if (!user) {
        observer.next(false);
        observer.complete();
        return;
      }

      const currentPortfolio = this.portfolioSubject.value;
      const stock = currentPortfolio?.stocks.find(s => s.symbol === symbol.toUpperCase());

      if (!stock || stock.shares < shares) {
        observer.next(false);
        observer.complete();
        return;
      }

      const totalAmount = shares * pricePerShare;
      const costBasis = shares * stock.averageCost;
      const realizedGainLoss = totalAmount - costBasis;

      const transaction: Transaction = {
        id: this.generateId(),
        userId: user.id,
        stockSymbol: symbol.toUpperCase(),
        type: TransactionType.SELL,
        shares,
        pricePerShare,
        totalAmount,
        fees: 0,
        date: new Date(),
        realizedGainLoss
      };

      const currentTransactions = this.transactionsSubject.value;
      this.transactionsSubject.next([...currentTransactions, transaction]);

      // Met à jour le budget
      this.authService.updateBudget(user.currentBudget + totalAmount);

      this.saveTransactions();
      this.updatePortfolio();

      // Émettre l'événement
      this.eventsSubject.next({
        type: PortfolioEventType.SELL,
        stockSymbol: symbol.toUpperCase(),
        quantity: shares,
        price: pricePerShare,
        totalAmount: totalAmount,
        timestamp: new Date()
      });

      observer.next(true);
      observer.complete();
    });
  }

  /**
   * Retourne le résumé des transactions
   */
  getTransactionSummary(): Observable<TransactionSummary> {
    return this.transactions$.pipe(
      map(transactions => {
        const summary: TransactionSummary = {
          totalBuys: 0,
          totalSells: 0,
          totalInvested: 0,
          totalRealizedGainLoss: 0,
          numberOfTransactions: transactions.length
        };

        transactions.forEach(transaction => {
          if (transaction.type === TransactionType.BUY) {
            summary.totalBuys++;
            summary.totalInvested += transaction.totalAmount;
          } else {
            summary.totalSells++;
            summary.totalRealizedGainLoss += (transaction.realizedGainLoss || 0);
          }
        });

        return summary;
      })
    );
  }

  /**
   * Exporte l'historique en JSON
   */
  exportHistory(): string {
    const transactions = this.transactionsSubject.value;
    return JSON.stringify({
      exportDate: new Date(),
      transactions,
      portfolio: this.portfolioSubject.value
    }, null, 2);
  }

  /**
   * Génère un ID unique
   */
  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Efface les données utilisateur
   */
  private clearUserData(): void {
    this.portfolioSubject.next(null);
    this.transactionsSubject.next([]);
    this.alertsSubject.next([]);
  }
}
