import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { DashboardComponent } from './components/dashboard/dashboard.component';
import { PortfolioListComponent } from './components/portfolio-list/portfolio-list.component';
import { BuyStockComponent } from './components/buy-stock/buy-stock.component';
import { SellStockComponent } from './components/sell-stock/sell-stock.component';
import { TransactionHistoryComponent } from './components/transaction-history/transaction-history.component';
import { AuthGuard } from '../shared/guards/auth.guard';

const routes: Routes = [
  { path: '', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'portfolio', component: PortfolioListComponent, canActivate: [AuthGuard] },
  { path: 'buy', component: BuyStockComponent, canActivate: [AuthGuard] },
  { path: 'sell', component: SellStockComponent, canActivate: [AuthGuard] },
  { path: 'history', component: TransactionHistoryComponent, canActivate: [AuthGuard] },
  { path: 'alerts', loadComponent: () => import('./components/alert-management/alert-management.component').then(m => m.AlertManagementComponent), canActivate: [AuthGuard] }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PortfolioRoutingModule { }
