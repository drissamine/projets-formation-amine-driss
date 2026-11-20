import { Injectable } from '@angular/core';
import { Observable, combineLatest } from 'rxjs';
import { map } from 'rxjs/operators';
import { PortfolioService } from './portfolio.service';
import { PriceService } from './price.service';


export interface AllocationData {
  name: string;
  value: number;
  percentage: number;
}

export interface GainLossData {
  amount: number;
  percentage: number;
}

export interface StockPerformance {
  symbol: string;
  gainLossAmount: number;
  gainLossPercentage: number;
  averagePrice: number;
  currentPrice: number;
  quantity: number;
}

export interface PerformanceMetrics {
  totalReturn: number;
  currentValue: number;
  totalInvested: number;
  weightedPerformance: number;
  volatility: number;
}

export interface VolatilityData {
  symbol: string;
  volatility: number;
  risk: string;
}

export interface RecommendedAllocation {
  conservative: { [key: string]: number };
  balanced: { [key: string]: number };
  aggressive: { [key: string]: number };
}

export interface PortfolioHistoryData {
  date: Date;
  value: number;
  invested: number;
}

@Injectable({
  providedIn: 'root'
})
export class PerformanceService {

  constructor(
    private portfolioService: PortfolioService,
    private priceService: PriceService
  ) { }

  getTotalValue(): Observable<number> {
    return combineLatest([
      this.portfolioService.portfolio$,
      this.priceService.getAllStockPrices()
    ]).pipe(
      map(([portfolio, prices]) => {
        if (!portfolio) return 0;
        return portfolio.stocks.reduce((total, item) => {
          const currentPrice = prices[item.symbol]?.price || item.averageCost;
          return total + (currentPrice * item.shares);
        }, 0);
      })
    );
  }

  getTotalInvested(): Observable<number> {
    return this.portfolioService.portfolio$.pipe(
      map(portfolio => {
        if (!portfolio) return 0;
        return portfolio.stocks.reduce((total, item) => {
          return total + (item.averageCost * item.shares);
        }, 0);
      })
    );
  }

  getGlobalGainLoss(): Observable<GainLossData> {
    return combineLatest([
      this.getTotalInvested(),
      this.getTotalValue()
    ]).pipe(
      map(([invested, current]) => {
        const amount = current - invested;
        const percentage = invested > 0 ? (amount / invested) * 100 : 0;
        return {
          amount,
          percentage
        };
      })
    );
  }

  getTopPerformers(): Observable<{ top: StockPerformance[], worst: StockPerformance[] }> {
    return combineLatest([
      this.portfolioService.portfolio$,
      this.priceService.getAllStockPrices()
    ]).pipe(
      map(([portfolio, prices]) => {
        if (!portfolio) return { top: [], worst: [] };

        const performances: StockPerformance[] = portfolio.stocks.map(item => {
          const currentPrice = prices[item.symbol]?.price || item.averageCost;
          const currentValue = currentPrice * item.shares;
          const investedValue = item.averageCost * item.shares;
          const gainLossAmount = currentValue - investedValue;
          const gainLossPercentage = investedValue > 0 ? ((currentValue - investedValue) / investedValue) * 100 : 0;

          return {
            symbol: item.symbol,
            gainLossAmount,
            gainLossPercentage,
            averagePrice: item.averageCost,
            currentPrice,
            quantity: item.shares
          };
        });

        // Trier par performance (pourcentage)
        const sorted = performances.sort((a, b) => b.gainLossPercentage - a.gainLossPercentage);

        return {
          top: sorted.slice(0, Math.min(3, sorted.length)),
          worst: sorted.slice(-Math.min(3, sorted.length)).reverse()
        };
      })
    );
  }

  getPortfolioHistory(): Observable<PortfolioHistoryData[]> {
    return combineLatest([
      this.portfolioService.transactions$,
      this.portfolioService.portfolio$,
      this.priceService.getAllStockPrices()
    ]).pipe(
      map(([transactions, portfolio, prices]) => {
        if (transactions.length === 0 && (!portfolio || portfolio.stocks.length === 0)) {
          return [];
        }

        const holdings = portfolio ? portfolio.stocks : [];

        // Trier les transactions par date
        const sortedTransactions = [...transactions].sort((a, b) => a.date.getTime() - b.date.getTime());

        // Générer des points de données pour l'historique
        const historyPoints: PortfolioHistoryData[] = [];
        const holdingsMap = new Map<string, { shares: number; averageCost: number }>();

        // Point de départ (portefeuille vide)
        const startDate = new Date();
        startDate.setMonth(startDate.getMonth() - 6); // 6 mois en arrière
        historyPoints.push({
          date: new Date(startDate),
          value: 0,
          invested: 0
        });

        // Traiter chaque transaction et créer des points intermédiaires
        sortedTransactions.forEach((transaction, index) => {
          // Mettre à jour les holdings
          const symbol = transaction.stockSymbol;
          const existing = holdingsMap.get(symbol) || { shares: 0, averageCost: 0 };

          if (transaction.type === 'BUY') {
            const newShares = existing.shares + transaction.shares;
            const newAverageCost = ((existing.shares * existing.averageCost) + (transaction.shares * transaction.pricePerShare)) / newShares;
            holdingsMap.set(symbol, { shares: newShares, averageCost: newAverageCost });
          } else if (transaction.type === 'SELL') {
            // Pour la vente, on garde le prix moyen mais on réduit la quantité
            existing.shares -= transaction.shares;
            if (existing.shares <= 0) {
              holdingsMap.delete(symbol);
            } else {
              holdingsMap.set(symbol, existing);
            }
          }

          // Calculer la valeur totale et investie à ce point
          let totalValue = 0;
          let totalInvested = 0;

          holdingsMap.forEach((holding, sym) => {
            const currentPrice = prices[sym]?.price || holding.averageCost;
            totalValue += currentPrice * holding.shares;
            totalInvested += holding.averageCost * holding.shares;
          });

          historyPoints.push({
            date: new Date(transaction.date),
            value: totalValue,
            invested: totalInvested
          });
        });

        // Ajouter le point actuel
        let currentValue = 0;
        let currentInvested = 0;

        holdings.forEach(holding => {
          const currentPrice = prices[holding.symbol]?.price || holding.averageCost;
          currentValue += currentPrice * holding.shares;
          currentInvested += holding.averageCost * holding.shares;
        });

        historyPoints.push({
          date: new Date(),
          value: currentValue,
          invested: currentInvested
        });

        // Générer des points intermédiaires pour un graphique plus fluide (tous les 7 jours)
        const smoothedHistory: PortfolioHistoryData[] = [];
        const daysBetween = 7;

        if (historyPoints.length > 1) {
          for (let i = 0; i < historyPoints.length - 1; i++) {
            const current = historyPoints[i];
            const next = historyPoints[i + 1];
            const daysDiff = Math.floor((next.date.getTime() - current.date.getTime()) / (1000 * 60 * 60 * 24));

            if (daysDiff <= daysBetween) {
              smoothedHistory.push(current);
            } else {
              // Ajouter des points intermédiaires
              smoothedHistory.push(current);
              const numPoints = Math.floor(daysDiff / daysBetween);
              for (let j = 1; j <= numPoints; j++) {
                const ratio = j / (numPoints + 1);
                const interpolatedDate = new Date(current.date.getTime() + (next.date.getTime() - current.date.getTime()) * ratio);
                const interpolatedValue = current.value + (next.value - current.value) * ratio;
                const interpolatedInvested = current.invested + (next.invested - current.invested) * ratio;

                smoothedHistory.push({
                  date: interpolatedDate,
                  value: interpolatedValue,
                  invested: interpolatedInvested
                });
              }
            }
          }
          smoothedHistory.push(historyPoints[historyPoints.length - 1]);
        } else {
          smoothedHistory.push(...historyPoints);
        }

        return smoothedHistory;
      })
    );
  }

  getAllocation(): Observable<AllocationData[]> {
    return combineLatest([
      this.portfolioService.portfolio$,
      this.priceService.getAllStockPrices()
    ]).pipe(
      map(([portfolio, prices]) => {
        if (!portfolio) return [];
        const holdings = portfolio.stocks;

        // Calculer la valeur totale du portefeuille
        const totalValue = holdings.reduce((total, item) => {
          const currentPrice = prices[item.symbol]?.price || item.averageCost;
          return total + (currentPrice * item.shares);
        }, 0);

        return holdings.map(item => {
          const currentPrice = prices[item.symbol]?.price || item.averageCost;
          const value = currentPrice * item.shares;
          const percentage = totalValue > 0 ? (value / totalValue) * 100 : 0;

          return {
            name: item.symbol,
            value,
            percentage
          };
        });
      })
    );
  }

  getPerformanceMetrics(): Observable<PerformanceMetrics> {
    return combineLatest([
      this.getTotalValue(),
      this.getTotalInvested(),
      this.getGlobalGainLoss()
    ]).pipe(
      map(([currentValue, totalInvested, gainLoss]) => {
        const totalReturn = gainLoss.percentage;
        const weightedPerformance = totalReturn; // Pour l'instant, même valeur

        // Calculer une volatilité simulée (valeur fictive pour l'exemple)
        const volatility = Math.random() * 20 + 5; // Entre 5% et 25%

        return {
          totalReturn,
          currentValue,
          totalInvested,
          weightedPerformance,
          volatility
        };
      })
    );
  }

  getVolatilityData(): Observable<VolatilityData[]> {
    return this.portfolioService.portfolio$.pipe(
      map(portfolio => {
        if (!portfolio) return [];
        return portfolio.stocks.map(holding => {
          // Calculer une volatilité simulée basée sur le symbole
          const baseVolatility = (holding.symbol.length * 2) + 5; // Simulation simple
          const volatility = Math.min(baseVolatility, 30); // Max 30%

          let risk: string;
          if (volatility < 10) risk = 'low';
          else if (volatility < 20) risk = 'medium';
          else risk = 'high';

          return {
            symbol: holding.symbol,
            volatility,
            risk
          };
        });
      })
    );
  }

  getStockPerformanceStats(): Observable<{ topPerformers: StockPerformance[]; worstPerformers: StockPerformance[] }> {
    return this.getTopPerformers().pipe(
      map(result => ({
        topPerformers: result.top,
        worstPerformers: result.worst
      }))
    );
  }

  getRecommendedAllocation(age: number, riskTolerance: string): RecommendedAllocation {
    // Logique simplifiée pour les allocations recommandées
    const conservative = {
      'Actions': 30,
      'Obligations': 50,
      'Liquidités': 20
    };

    const balanced = {
      'Actions': 60,
      'Obligations': 30,
      'Liquidités': 10
    };

    const aggressive = {
      'Actions': 80,
      'Obligations': 15,
      'Liquidités': 5
    };

    // Ajuster selon l'âge (plus conservateur si âge élevé)
    if (age > 50) {
      conservative.Actions = Math.max(20, conservative.Actions - (age - 50));
      conservative.Obligations += (age - 50) / 2;
      conservative.Liquidités += (age - 50) / 2;

      balanced.Actions = Math.max(40, balanced.Actions - (age - 50));
      balanced.Obligations += (age - 50) / 2;

      aggressive.Actions = Math.max(60, aggressive.Actions - (age - 50));
      aggressive.Obligations += (age - 50) / 2;
    }

    return {
      conservative,
      balanced,
      aggressive
    };
  }
}
