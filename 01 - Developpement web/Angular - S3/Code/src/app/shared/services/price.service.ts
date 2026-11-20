import { Injectable } from '@angular/core';
import { Observable, interval, BehaviorSubject, of } from 'rxjs';
import { map, startWith, switchMap, catchError } from 'rxjs/operators';
import { Stock, StockPrice, HistoricalPrice } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class PriceService {
  // Prix de base pour chaque action (comme spécifié dans le TP)
  private readonly BASE_PRICES: { [key: string]: number } = {
    'AAPL': 185.50,
    'GOOG': 140.75,
    'MSFT': 380.20,
    'AMZN': 175.40,
    'TESLA': 245.30,
    'SPX500': 4500.00 // Pour la comparaison
  };

  // Stockage des prix courants avec timestamp
  private stockPrices = new BehaviorSubject<{ [key: string]: StockPrice }>({});

  // Variables pour simuler la volatilité
  private volatilityFactors: { [key: string]: number } = {};

  constructor() {
    this.initializeStockPrices();
    this.startPriceUpdates();
  }

  /**
   * Initialise les prix de base
   */
  private initializeStockPrices(): void {
    const prices: { [key: string]: StockPrice } = {};

    Object.keys(this.BASE_PRICES).forEach(symbol => {
      const basePrice = this.BASE_PRICES[symbol];
      prices[symbol] = {
        symbol,
        price: basePrice,
        change: 0,
        changePercent: 0,
        timestamp: new Date()
      };
      // Initialise les facteurs de volatilité
      this.volatilityFactors[symbol] = this.generateVolatilityFactor();
    });

    this.stockPrices.next(prices);
  }

  /**
   * Démarre les mises à jour périodiques des prix
   */
  private startPriceUpdates(): void {
    // Mise à jour toutes les 30 secondes pour simuler les fluctuations du marché
    interval(30000).pipe(
      switchMap(() => this.updateAllPrices())
    ).subscribe();
  }

  /**
   * Met à jour tous les prix avec des variations aléatoires
   */
  private updateAllPrices(): Observable<{ [key: string]: StockPrice }> {
    const currentPrices = { ...this.stockPrices.value };
    const updatedPrices: { [key: string]: StockPrice } = {};

    Object.keys(currentPrices).forEach(symbol => {
      const currentPrice = currentPrices[symbol];
      const newPrice = this.calculateNewPrice(currentPrice.price, symbol);
      const change = newPrice - currentPrice.price;
      const changePercent = (change / currentPrice.price) * 100;

      updatedPrices[symbol] = {
        symbol,
        price: newPrice,
        change,
        changePercent,
        timestamp: new Date()
      };

      // Met à jour le facteur de volatilité pour la prochaine itération
      this.volatilityFactors[symbol] = this.generateVolatilityFactor();
    });

    this.stockPrices.next(updatedPrices);
    return of(updatedPrices);
  }

  /**
   * Calcule un nouveau prix basé sur le prix actuel et la volatilité
   */
  private calculateNewPrice(currentPrice: number, symbol: string): number {
    const volatilityFactor = this.volatilityFactors[symbol] || 0.01;

    // Détermine une tendance aléatoire (Bearish -1, Neutral 0, Bullish 1)
    const rand = Math.random();
    let trend = 0;
    if (rand < 0.4) {
      trend = -1; // 40% de chance de baisse
    } else if (rand > 0.6) {
      trend = 1;  // 40% de chance de hausse
    }
    // Sinon 20% de chance de stagnation (Neutral)

    // Variation de base (-0.5 à 0.5)
    let randomComponent = (Math.random() - 0.5);

    // Accentuation de la baisse ou de la hausse selon la tendance
    if (trend === -1) {
      randomComponent = -Math.abs(Math.random()); // Force négatif
    } else if (trend === 1) {
      randomComponent = Math.abs(Math.random()); // Force positif
    }

    const variation = randomComponent * 2 * volatilityFactor * currentPrice;
    const newPrice = Math.max(0.01, currentPrice + variation);
    return Math.round(newPrice * 100) / 100;
  }

  /**
   * Génère un facteur de volatilité aléatoire (±2% comme spécifié dans le TP)
   */
  private generateVolatilityFactor(): number {
    return 0.01 + Math.random() * 0.01; // Entre 1% et 2%
  }

  /**
   * Retourne un Observable des prix de toutes les actions
   */
  getAllStockPrices(): Observable<{ [key: string]: StockPrice }> {
    return this.stockPrices.asObservable();
  }

  /**
   * Retourne le prix d'une action spécifique
   */
  getStockPrice(symbol: string): Observable<StockPrice | null> {
    return this.stockPrices.pipe(
      map(prices => prices[symbol] || null),
      catchError(() => of(null))
    );
  }

  /**
   * Retourne les informations d'une action complète
   */
  getStockInfo(symbol: string): Observable<Stock | null> {
    return this.getStockPrice(symbol).pipe(
      map(price => {
        if (!price) return null;

        return {
          symbol: price.symbol,
          name: this.getStockName(symbol),
          currentPrice: price.price,
          previousPrice: price.price - price.change,
          change: price.change,
          changePercent: price.changePercent,
          lastUpdated: price.timestamp
        };
      })
    );
  }

  /**
   * Retourne le nom complet de l'action
   */
  private getStockName(symbol: string): string {
    const names: { [key: string]: string } = {
      'AAPL': 'Apple Inc.',
      'GOOG': 'Alphabet Inc.',
      'MSFT': 'Microsoft Corporation',
      'AMZN': 'Amazon.com Inc.',
      'TESLA': 'Tesla Inc.',
      'SPX500': 'S&P 500 Index'
    };
    return names[symbol] || symbol;
  }

  /**
   * Simule l'obtention de données historiques
   */
  getHistoricalData(symbol: string, days: number = 30): Observable<HistoricalPrice[]> {
    return this.getStockPrice(symbol).pipe(
      map(currentPrice => {
        if (!currentPrice) return [];

        const historicalData: HistoricalPrice[] = [];
        let currentPriceForHistory = currentPrice.price;

        // Génère des données historiques basées sur le prix actuel
        for (let i = days; i >= 0; i--) {
          const date = new Date();
          date.setDate(date.getDate() - i);

          // Variation journalière simulée
          const dailyVariation = (Math.random() - 0.5) * 0.05; // ±2.5% par jour
          const open = currentPriceForHistory;
          const close = Math.max(0.01, open * (1 + dailyVariation));
          const high = Math.max(open, close) * (1 + Math.random() * 0.02);
          const low = Math.min(open, close) * (1 - Math.random() * 0.02);

          historicalData.push({
            date,
            open: Math.round(open * 100) / 100,
            high: Math.round(high * 100) / 100,
            low: Math.round(low * 100) / 100,
            close: Math.round(close * 100) / 100,
            volume: Math.floor(Math.random() * 10000000) + 1000000
          });

          currentPriceForHistory = close;
        }

        return historicalData;
      })
    );
  }

  /**
   * Force une mise à jour des prix (pour les tests ou actions manuelles)
   */
  refreshPrices(): Observable<boolean> {
    return this.updateAllPrices().pipe(
      map(() => true),
      catchError(() => of(false))
    );
  }

  /**
   * Retourne la liste des symboles d'actions disponibles
   */
  getAvailableSymbols(): string[] {
    return Object.keys(this.BASE_PRICES);
  }

  /**
   * Vérifie si un symbole d'action existe
   */
  stockExists(symbol: string): boolean {
    return symbol.toUpperCase() in this.BASE_PRICES;
  }
}
