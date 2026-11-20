export interface Transaction {
  id: string;
  userId: string;
  stockSymbol: string;
  type: TransactionType;
  shares: number;
  pricePerShare: number;
  totalAmount: number;
  fees: number;
  date: Date;
  notes?: string;
  realizedGainLoss?: number; // Pour les ventes uniquement
}

export enum TransactionType {
  BUY = 'BUY',
  SELL = 'SELL'
}

export interface BuyTransaction extends Transaction {
  type: TransactionType.BUY;
}

export interface SellTransaction extends Transaction {
  type: TransactionType.SELL;
  realizedGainLoss: number;
}

export interface TransactionSummary {
  totalBuys: number;
  totalSells: number;
  totalInvested: number;
  totalRealizedGainLoss: number;
  numberOfTransactions: number;
}
