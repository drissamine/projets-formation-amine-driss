import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { PortfolioRoutingModule } from './portfolio-routing-module';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { PortfolioListComponent } from './components/portfolio-list/portfolio-list.component';
import { BuyStockComponent } from './components/buy-stock/buy-stock.component';
import { SellStockComponent } from './components/sell-stock/sell-stock.component';
import { TransactionHistoryComponent } from './components/transaction-history/transaction-history.component';


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    PortfolioRoutingModule,
    DashboardComponent,
    PortfolioListComponent,
    BuyStockComponent,
    SellStockComponent,
    TransactionHistoryComponent
  ]
})
export class PortfolioModule { }
