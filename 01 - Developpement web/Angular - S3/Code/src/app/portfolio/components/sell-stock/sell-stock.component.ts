import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { Observable, combineLatest } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';
import { Portfolio, PortfolioStock } from '../../../shared/models/portfolio.model';
import { User } from '../../../shared/models/user.model';
import { PortfolioService } from '../../../shared/services/portfolio.service';
import { AuthService } from '../../../shared/services/auth.service';
import { PriceService } from '../../../shared/services/price.service';

interface SellFormData {
  symbol: string;
  shares: number;
  pricePerShare: number;
  totalProceeds: number;
  realizedGainLoss: number;
  date: Date;
}

import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-sell-stock',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './sell-stock.component.html',
  styleUrl: './sell-stock.component.scss'
})
export class SellStockComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  sellForm: FormGroup;
  user$: Observable<User | null>;
  availableStocks$!: Observable<PortfolioStock[]>;
  currentPrice = 0;
  priceChange = 0;
  priceChangePercent = 0;
  ownedShares = 0;
  averageCost = 0; // Propriété ajoutée
  isLoading = false;
  isSubmitting = false;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private portfolioService: PortfolioService,
    private authService: AuthService,
    private priceService: PriceService
  ) {
    this.user$ = this.authService.currentUser$;
    this.sellForm = this.fb.group({
      symbol: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(5)]],
      shares: ['', [Validators.required, Validators.min(1)]],
      pricePerShare: ['', [Validators.required, Validators.min(0.01)]],
      date: [this.formatDateForInput(new Date()), [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Charge les actions possedées
    this.availableStocks$ = this.portfolioService.portfolio$.pipe(
      map(portfolio => portfolio?.stocks || [])
    );

    // Écoute les changements de symbole
    this.sellForm.get('symbol')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(symbol => {
        if (symbol) {
          this.updateStockInfo(symbol.toUpperCase());
        }
      });

    // Recalcule les données quand le prix change
    this.sellForm.get('pricePerShare')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        // Les calculs se font via les getters
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private updateStockInfo(symbol: string): void {
    // Met à jour le prix
    this.priceService.getStockPrice(symbol).pipe(
      takeUntil(this.destroy$)
    ).subscribe(price => {
      if (price) {
        this.currentPrice = price.price;
        this.priceChange = price.change;
        this.priceChangePercent = price.changePercent;
        this.sellForm.patchValue({ pricePerShare: price.price }, { emitEvent: false });
      }
    });

    // Met à jour le nombre d'actions possedées
    this.availableStocks$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(stocks => {
      const stock = stocks.find(s => s.symbol === symbol);
      this.ownedShares = stock ? stock.shares : 0;
      this.averageCost = stock ? stock.averageCost : 0; // Update averageCost
    });
  }

  onSubmit(): void {
    if (this.sellForm.invalid) {
      return;
    }

    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';

    const formData: SellFormData = {
      symbol: this.sellForm.value.symbol.toUpperCase(),
      shares: parseInt(this.sellForm.value.shares),
      pricePerShare: parseFloat(this.sellForm.value.pricePerShare),
      totalProceeds: parseInt(this.sellForm.value.shares) * parseFloat(this.sellForm.value.pricePerShare),
      realizedGainLoss: 0, // Calculé côté serveur
      date: new Date(this.sellForm.value.date)
    };

    // Vérifie que l'utilisateur possede assez d'actions
    if (formData.shares > this.ownedShares) {
      this.errorMessage = `Vous ne possédez que ${this.ownedShares} actions ${formData.symbol}.`;
      this.isSubmitting = false;
      return;
    }

    // Exécute la vente
    this.portfolioService.sellStock(
      formData.symbol,
      formData.shares,
      formData.pricePerShare
    ).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (success) => {
        this.isSubmitting = false;
        if (success) {
          this.successMessage = `Vente de ${formData.shares} actions ${formData.symbol} réussie pour ${this.formatCurrency(formData.totalProceeds)}.`;
          this.sellForm.reset({ date: new Date() });
          this.ownedShares = 0;
          this.averageCost = 0;
        } else {
          this.errorMessage = 'Erreur lors de la vente. Veuillez réessayer.';
        }
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = 'Erreur lors de la vente: ' + (error.message || 'Erreur inconnue');
      }
    });
  }

  // Getters pour les calculs dynamiques
  get totalProceeds(): number {
    const shares = this.sellForm.get('shares')?.value || 0;
    const price = this.sellForm.get('pricePerShare')?.value || 0;
    return shares * price;
  }

  // Nouveaux Getters
  get potentialGainLoss(): number {
    const shares = this.sellForm.get('shares')?.value || 0;
    const price = this.sellForm.get('pricePerShare')?.value || 0;
    const costBasis = shares * this.averageCost;
    return (shares * price) - costBasis;
  }

  get potentialGainLossPercent(): number {
    const shares = this.sellForm.get('shares')?.value || 0;
    const costBasis = shares * this.averageCost;
    if (costBasis === 0) return 0;
    return (this.potentialGainLoss / costBasis) * 100;
  }

  get canSell(): boolean {
    return this.sellForm.valid &&
      this.sellForm.get('shares')?.value <= this.ownedShares &&
      this.sellForm.get('shares')?.value > 0;
  }

  // Utilitaires
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }

  // Helpers pour les templates
  getFieldError(fieldName: string): string {
    const control = this.sellForm.get(fieldName);
    if (!control || !control.touched || !control.errors) {
      return '';
    }

    if (control.errors['required']) {
      return 'Ce champ est obligatoire';
    }

    if (control.errors['min']) {
      return `Valeur minimale: ${control.errors['min'].min}`;
    }

    if (control.errors['max']) {
      return `Vous ne possédez que ${control.errors['max'].max} actions`;
    }

    if (control.errors['pattern']) {
      return 'Format invalide';
    }

    return 'Champ invalide';
  }

  getChangeClass(value: number): string {
    if (value > 0) return 'text-success';
    if (value < 0) return 'text-danger';
    return 'text-secondary';
  }

  formatPercentage(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100);
  }

  refreshPrices(): void {
    this.priceService.refreshPrices().subscribe({
      next: () => {
        const symbol = this.sellForm.get('symbol')?.value;
        if (symbol) {
          this.updateStockInfo(symbol.toUpperCase());
        }
      },
      error: (error) => {
        console.error('Erreur lors de la mise à jour des prix:', error);
      }
    });
  }

  resetForm(): void {
    this.sellForm.reset({ date: this.formatDateForInput(new Date()) });
    this.ownedShares = 0;
    this.averageCost = 0;
    this.currentPrice = 0;
    this.successMessage = '';
    this.errorMessage = '';
  }

  private formatDateForInput(date: Date): string {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
  }
}
