export interface Stock {
  symbol: string;
  name: string;
  currentPrice: number;
  previousPrice: number;
  change: number;
  changePercent: number;
  lastUpdated: Date;
}

export interface StockPrice {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  timestamp: Date;
}

export interface StockQuote {
  symbol: string;
  price: number;
  volume: number;
  marketCap: number;
  peRatio?: number;
  dividendYield?: number;
}

export interface HistoricalPrice {
  date: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
