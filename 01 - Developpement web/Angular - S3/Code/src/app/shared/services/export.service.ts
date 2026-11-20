import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { Observable } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';
import { PortfolioService } from './portfolio.service';
import { AlertService } from './alert.service';

export interface ExportData {
  portfolio: {
    holdings: any[];
    transactions: any[];
    performance: any;
  };
  alerts: any[];
  user: any;
  exportDate: string;
  version: string;
}

@Injectable({
  providedIn: 'root'
})
export class ExportService {
  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private portfolioService: PortfolioService,
    private alertService: AlertService
  ) { }

  exportPortfolioHistory(): void {
    if (!isPlatformBrowser(this.platformId)) {
      console.warn('Export is only available in browser environment');
      return;
    }

    const exportData = this.generateExportData();
    const jsonString = JSON.stringify(exportData, null, 2);
    const fileName = `portfolio_history_${this.formatDate(new Date())}.json`;

    this.downloadJsonFile(jsonString, fileName);
  }

  exportPortfolioAsCsv(): void {
    if (!isPlatformBrowser(this.platformId)) {
      console.warn('Export is only available in browser environment');
      return;
    }

    const transactions = this.getTransactionsData();
    const csvContent = this.convertToCsv(transactions);
    const fileName = `portfolio_transactions_${this.formatDate(new Date())}.csv`;

    this.downloadCsvFile(csvContent, fileName);
  }

  exportPortfolioAsPdf(): Observable<Blob> {
    // Cette fonction retournerait un Observable pour générer un PDF
    // Pour cette démo, on va simuler le comportement
    return new Observable(observer => {
      const exportData = this.generateExportData();
      const pdfContent = this.generatePdfContent(exportData);

      const blob = new Blob([pdfContent], { type: 'application/pdf' });
      observer.next(blob);
      observer.complete();
    });
  }

  exportPortfolioSummary(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    const summary = this.generateSummaryReport();
    const jsonString = JSON.stringify(summary, null, 2);
    const fileName = `portfolio_summary_${this.formatDate(new Date())}.json`;

    this.downloadJsonFile(jsonString, fileName);
  }

  private generateExportData(): ExportData {
    const holdings = this.getHoldingsData();
    const transactions = this.getTransactionsData();
    const performance = this.calculatePerformanceSummary(holdings, transactions);
    const alerts = this.getAlertsData();

    return {
      portfolio: {
        holdings,
        transactions,
        performance
      },
      alerts,
      user: this.getUserData(),
      exportDate: new Date().toISOString(),
      version: '1.0.0'
    };
  }

  private getHoldingsData(): any[] {
    const holdings: any[] = [];

    this.portfolioService.portfolio$.subscribe(portfolio => {
      if (portfolio) {
        portfolio.stocks.forEach(holding => {
          holdings.push({
            ...holding,
            currentValue: holding.shares * this.getCurrentPrice(holding.symbol),
            unrealizedGain: (this.getCurrentPrice(holding.symbol) - holding.averageCost) * holding.shares,
            unrealizedGainPercent: ((this.getCurrentPrice(holding.symbol) - holding.averageCost) / holding.averageCost) * 100
          });
        });
      }
    });

    return holdings;
  }

  private getTransactionsData(): any[] {
    const transactions: any[] = [];

    this.portfolioService.transactions$.subscribe(currentTransactions => {
      currentTransactions.forEach(transaction => {
        transactions.push({
          ...transaction,
          formattedDate: transaction.date.toLocaleString('fr-FR'),
          totalValue: transaction.shares * transaction.pricePerShare,
          transactionType: transaction.type === 'BUY' ? 'Achat' : 'Vente'
        });
      });
    });

    return transactions;
  }

  private getAlertsData(): any[] {
    const alerts: any[] = [];

    this.alertService.alerts$.subscribe(currentAlerts => {
      currentAlerts.forEach(alert => {
        alerts.push({
          ...alert,
          formattedCreatedAt: alert.id ? new Date(parseInt(alert.id)).toLocaleString('fr-FR') : '',
          formattedTriggeredAt: alert.triggeredAt ? alert.triggeredAt.toLocaleString('fr-FR') : ''
        });
      });
    });

    return alerts;
  }

  private getUserData(): any {
    // Récupérer les données utilisateur depuis le localStorage ou le service d'auth
    const userData = localStorage.getItem('currentUser');
    return userData ? JSON.parse(userData) : null;
  }

  private calculatePerformanceSummary(holdings: any[], transactions: any[]): any {
    const totalInvested = transactions
      .filter(t => t.type === 'BUY')
      .reduce((sum, t) => sum + (t.quantity * t.pricePerShare), 0);

    const totalCurrentValue = holdings
      .reduce((sum, h) => sum + h.currentValue, 0);

    const totalRealizedGains = transactions
      .filter(t => t.type === 'SELL')
      .reduce((sum, t) => {
        // Calcul simplifié des gains réalisés
        return sum + ((t.pricePerShare - this.getAverageBuyPrice(t.symbol, transactions)) * t.shares);
      }, 0);

    const totalUnrealizedGains = holdings
      .reduce((sum, h) => sum + h.unrealizedGain, 0);

    const totalReturn = totalCurrentValue + totalRealizedGains - totalInvested;
    const totalReturnPercent = totalInvested > 0 ? (totalReturn / totalInvested) * 100 : 0;

    return {
      totalInvested,
      totalCurrentValue,
      totalRealizedGains,
      totalUnrealizedGains,
      totalReturn,
      totalReturnPercent,
      numberOfHoldings: holdings.length,
      numberOfTransactions: transactions.length,
      diversificationScore: this.calculateDiversificationScore(holdings)
    };
  }

  private generateSummaryReport(): any {
    // ... (rest of method remains mostly same but uses refactored helper methods)
    const holdings = this.getHoldingsData();
    const transactions = this.getTransactionsData();
    const performance = this.calculatePerformanceSummary(holdings, transactions);

    return {
      summary: {
        exportDate: new Date().toISOString(),
        portfolioValue: performance.totalCurrentValue,
        totalReturn: performance.totalReturn,
        totalReturnPercent: performance.totalReturnPercent,
        numberOfHoldings: performance.numberOfHoldings,
        numberOfTransactions: performance.numberOfTransactions
      },
      topPerformers: holdings
        .sort((a, b) => b.unrealizedGainPercent - a.unrealizedGainPercent)
        .slice(0, 5),
      recentTransactions: transactions
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, 10),
      allocation: holdings.map(h => ({
        symbol: h.symbol,
        percentage: (h.currentValue / performance.totalCurrentValue) * 100
      }))
    };
  }

  private convertToCsv(transactions: any[]): string {
    if (transactions.length === 0) return 'Date,Type,Symbole,Quantité,Prix,Valeur Totale\n';

    const headers = ['Date', 'Type', 'Symbole', 'Quantité', 'Prix Unitaire', 'Valeur Totale'];
    const csvRows = [headers.join(',')];

    transactions.forEach(transaction => {
      const row = [
        transaction.formattedDate,
        transaction.transactionType,
        transaction.stockSymbol, // Changed from symbol
        transaction.shares.toString(), // Changed from quantity
        transaction.pricePerShare.toFixed(2), // Changed from price
        transaction.totalValue.toFixed(2)
      ];
      csvRows.push(row.join(','));
    });

    return csvRows.join('\n');
  }

  private generatePdfContent(data: ExportData): string {
    // Génération simplifiée de contenu PDF
    return `PORTFOLIO EXPORT REPORT
Generated: ${data.exportDate}
Version: ${data.version}

PORTFOLIO SUMMARY
================
Total Holdings: ${data.portfolio.holdings.length}
Total Transactions: ${data.portfolio.transactions.length}
Current Value: €${data.portfolio.performance.totalCurrentValue?.toFixed(2) || '0.00'}
Total Return: €${data.portfolio.performance.totalReturn?.toFixed(2) || '0.00'} (${data.portfolio.performance.totalReturnPercent?.toFixed(2) || '0.00'}%)

HOLDINGS
========
${data.portfolio.holdings.map(h =>
      `${h.symbol}: ${h.shares} shares @ €${h.averageCost.toFixed(2)} (Current: €${this.getCurrentPrice(h.symbol).toFixed(2)})`
    ).join('\n')}

RECENT TRANSACTIONS
==================
${data.portfolio.transactions
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, 10)
        .map(t => `${t.date.toLocaleDateString()} - ${t.transactionType} ${t.shares} ${t.stockSymbol} @ €${t.pricePerShare.toFixed(2)}`)
        .join('\n')}`;
  }

  private getCurrentPrice(symbol: string): number {
    const prices: { [key: string]: number } = {
      'AAPL': 185.50,
      'GOOG': 140.75,
      'MSFT': 380.20,
      'AMZN': 175.40,
      'TSLA': 245.30
    };
    return prices[symbol] || 0;
  }

  private getAverageBuyPrice(symbol: string, transactions: any[]): number {
    const buyTransactions = transactions.filter(t => t.stockSymbol === symbol && t.type === 'BUY');
    if (buyTransactions.length === 0) return 0;

    const totalValue = buyTransactions.reduce((sum, t) => sum + (t.shares * t.pricePerShare), 0);
    const totalQuantity = buyTransactions.reduce((sum, t) => sum + t.shares, 0);

    return totalQuantity > 0 ? totalValue / totalQuantity : 0;
  }

  private calculateDiversificationScore(holdings: any[]): number {
    if (holdings.length === 0) return 0;
    if (holdings.length === 1) return 10; // Faible diversification

    const totalValue = holdings.reduce((sum, h) => sum + h.currentValue, 0);
    const maxWeight = Math.max(...holdings.map(h => (h.currentValue / totalValue) * 100));

    // Score inversement proportionnel à la concentration
    return Math.max(0, 100 - maxWeight);
  }

  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  private downloadJsonFile(content: string, fileName: string): void {
    const blob = new Blob([content], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  private downloadCsvFile(content: string, fileName: string): void {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
    window.URL.revokeObjectURL(url);
  }
}
