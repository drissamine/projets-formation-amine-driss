import { Routes } from '@angular/router';
import { Login } from './shared/components/login/login';
import { AuthGuard } from './shared/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'portfolio', pathMatch: 'full' },
  { path: 'login', component: Login },
  {
    path: 'portfolio',
    loadChildren: () => import('./portfolio/portfolio-module').then(m => m.PortfolioModule),
    canActivate: [AuthGuard]
  }
];
