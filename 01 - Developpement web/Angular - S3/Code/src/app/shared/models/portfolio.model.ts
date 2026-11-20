import { Stock } from './stock.model';
import { Transaction } from './transaction.model';

export interface Portfolio {
  userId: string;
  stocks: PortfolioStock[];
  totalValue: number;
  totalInvested: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  performanceMetrics: PerformanceMetrics;
  lastUpdated: Date;
}

export interface PortfolioStock {
  symbol: string;
  shares: number;
  averageCost: number;
  currentPrice: number;
  totalValue: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  gainLossSincePurchase: number;
  gainLossSincePurchasePercent: number;
  allocationPercent: number;
  lastUpdated: Date;
}

export interface PerformanceMetrics {
  totalReturn: number; // Rendement total
  weightedReturn: number; // Performance pondérée
  volatility: number; // Volatilité simulée
  sharpeRatio?: number; // Ratio de Sharpe (si implémenté)
  beta?: number; // Bêta du portefeuille
  diversificationScore: number; // Score de diversification
  riskLevel: RiskLevel;
}

export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  VERY_HIGH = 'VERY_HIGH'
}

export interface AssetAllocation {
  stock: string;
  percentage: number;
  recommendedPercentage: number;
  deviation: number;
}

export interface PortfolioComparison {
  portfolioValue: number;
  sp500Value: number;
  portfolioReturn: number;
  sp500Return: number;
  outperformance: number;
}

export interface PortfolioAlert {
  id: string;
  userId: string;
  stockSymbol: string;
  alertType: AlertType;
  threshold: number;
  currentValue: number;
  isTriggered: boolean;
  message: string;
  createdAt: Date;
  triggeredAt?: Date;
}

export enum AlertType {
  PRICE_DROP = 'PRICE_DROP',
  PRICE_RISE = 'PRICE_RISE',
  GAIN_TARGET = 'GAIN_TARGET',
  LOSS_LIMIT = 'LOSS_LIMIT'
}

export interface PortfolioEvent {
  type: PortfolioEventType;
  stockSymbol: string;
  quantity: number;
  price: number;
  totalAmount: number;
  timestamp: Date;
}

export enum PortfolioEventType {
  BUY = 'BUY',
  SELL = 'SELL'
}
