import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class NavigationService {
  navigationItems = [
    {
      id: 'dashboard',
      title: 'Dashboard',
      icon: 'dashboard',
      route: '/dashboard',
      type: 'item'
    },
    {
      id: 'portfolio',
      title: 'Portfolio',
      icon: 'account_balance',
      route: '/portfolio',
      type: 'item'
    },
    {
      id: 'transactions',
      title: 'Transactions',
      icon: 'receipt',
      route: '/transactions',
      type: 'item'
    }
  ];

  getNavigationItems() {
    return this.navigationItems;
  }
}
