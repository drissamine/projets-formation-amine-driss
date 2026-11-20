import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';

export interface SPX500Data {
  date: Date;
  value: number;
  change: number;
  changePercent: number;
}

export interface ComparisonResult {
  portfolioReturn: number;
  spx500Return: number;
  outperformance: number;
  outperformancePercent: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  recommendation: string;
}

@Injectable({
  providedIn: 'root'
})
export class SPX500Service {
  private currentValue = 4750.00; // Valeur actuelle simulée du SPX500
  private historySubject = new BehaviorSubject<SPX500Data[]>([]);
  public history$ = this.historySubject.asObservable();

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      this.initializeHistory();
      this.startSimulation();
    }
  }

  private initializeHistory(): void {
    // Générer 30 jours d'historique
    const history: SPX500Data[] = [];
    let currentDate = new Date();
    let currentPrice = this.currentValue;

    for (let i = 30; i >= 0; i--) {
      const date = new Date(currentDate);
      date.setDate(date.getDate() - i);
      
      // Simuler la variation du SPX500 (±1% par jour en moyenne)
      const volatility = 0.01;
      const change = 1 + (Math.random() * volatility * 2 - volatility);
      currentPrice = currentPrice * change;
      
      const previousValue = i === 30 ? currentPrice : history[history.length - 1]?.value || currentPrice;
      const changeAmount = currentPrice - previousValue;
      const changePercent = previousValue > 0 ? (changeAmount / previousValue) * 100 : 0;

      history.push({
        date,
        value: parseFloat(currentPrice.toFixed(2)),
        change: parseFloat(changeAmount.toFixed(2)),
        changePercent: parseFloat(changePercent.toFixed(2))
      });
    }

    this.historySubject.next(history);
  }

  private startSimulation(): void {
    // Simuler les mises à jour du SPX500 toutes les 10 secondes
    setInterval(() => {
      this.updateSPX500Value();
    }, 10000);
  }

  private updateSPX500Value(): void {
    // Simuler la variation du SPX500 (±0.5% par mise à jour)
    const volatility = 0.005;
    const change = 1 + (Math.random() * volatility * 2 - volatility);
    this.currentValue = this.currentValue * change;
    
    const history = this.historySubject.value;
    const lastEntry = history[history.length - 1];
    const previousValue = lastEntry?.value || this.currentValue;
    const changeAmount = this.currentValue - previousValue;
    const changePercent = previousValue > 0 ? (changeAmount / previousValue) * 100 : 0;

    const newEntry: SPX500Data = {
      date: new Date(),
      value: parseFloat(this.currentValue.toFixed(2)),
      change: parseFloat(changeAmount.toFixed(2)),
      changePercent: parseFloat(changePercent.toFixed(2))
    };

    // Garder seulement les 30 derniers jours
    const updatedHistory = [...history.slice(-29), newEntry];
    this.historySubject.next(updatedHistory);
  }

  getCurrentValue(): number {
    return parseFloat(this.currentValue.toFixed(2));
  }

  getCurrentChange(): { change: number; changePercent: number } {
    const history = this.historySubject.value;
    const lastEntry = history[history.length - 1];
    const previousEntry = history[history.length - 2];
    
    if (!lastEntry || !previousEntry) {
      return { change: 0, changePercent: 0 };
    }

    return {
      change: lastEntry.change,
      changePercent: lastEntry.changePercent
    };
  }

  getHistory(days: number = 30): Observable<SPX500Data[]> {
    return this.history$.pipe(
      map(history => history.slice(-days))
    );
  }

  calculateReturn(period: '1D' | '1W' | '1M' | '3M' | '1Y'): number {
    const history = this.historySubject.value;
    if (history.length === 0) return 0;

    const currentValue = history[history.length - 1].value;
    let daysToSubtract: number;

    switch (period) {
      case '1D':
        daysToSubtract = 1;
        break;
      case '1W':
        daysToSubtract = 7;
        break;
      case '1M':
        daysToSubtract = 30;
        break;
      case '3M':
        daysToSubtract = 90;
        break;
      case '1Y':
        daysToSubtract = 365;
        break;
      default:
        daysToSubtract = 30;
    }

    const startIndex = Math.max(0, history.length - daysToSubtract - 1);
    const startValue = history[startIndex]?.value || currentValue;
    
    return ((currentValue - startValue) / startValue) * 100;
  }

  compareWithPortfolio(portfolioReturn: number): ComparisonResult {
    const spx500Return = this.calculateReturn('1M'); // Comparaison sur 1 mois
    const outperformance = portfolioReturn - spx500Return;
    const outperformancePercent = spx500Return !== 0 ? (outperformance / Math.abs(spx500Return)) * 100 : 0;

    let riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    let recommendation: string;

    if (Math.abs(outperformance) < 2) {
      riskLevel = 'LOW';
      recommendation = 'Performance similaire au marché. Stratégie équilibrée.';
    } else if (Math.abs(outperformance) < 5) {
      riskLevel = 'MEDIUM';
      recommendation = outperformance > 0 
        ? 'Bonne surperformance. Surveiller la concentration du portefeuille.'
        : 'Sous-performance modérée. Considérer la diversification.';
    } else {
      riskLevel = 'HIGH';
      recommendation = outperformance > 0 
        ? 'Excellente surperformance ! Surveiller le risque de concentration.'
        : 'Sous-performance importante. Réviser la stratégie d\'investissement.';
    }

    return {
      portfolioReturn: parseFloat(portfolioReturn.toFixed(2)),
      spx500Return: parseFloat(spx500Return.toFixed(2)),
      outperformance: parseFloat(outperformance.toFixed(2)),
      outperformancePercent: parseFloat(outperformancePercent.toFixed(2)),
      riskLevel,
      recommendation
    };
  }

  getBenchmarkData(): Observable<SPX500Data[]> {
    return this.history$;
  }
}
