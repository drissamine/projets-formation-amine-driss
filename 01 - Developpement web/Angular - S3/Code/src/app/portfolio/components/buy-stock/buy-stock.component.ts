import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { User } from '../../../shared/models/user.model';
import { PortfolioService } from '../../../shared/services/portfolio.service';
import { AuthService } from '../../../shared/services/auth.service';
import { PriceService } from '../../../shared/services/price.service';

interface BuyFormData {
  symbol: string;
  shares: number;
  pricePerShare: number;
  totalCost: number;
  date: Date;
}

import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-buy-stock',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './buy-stock.component.html',
  styleUrl: './buy-stock.component.scss'
})
export class BuyStockComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  buyForm!: FormGroup;
  user$: Observable<User | null>;
  availableSymbols: string[] = [];
  isLoading = false;
  isSubmitting = false;
  successMessage = '';
  errorMessage = '';

  // Prix de l'action sélectionnée
  currentPrice = 0;
  priceChange = 0;
  priceChangePercent = 0;

  constructor(
    private fb: FormBuilder,
    private portfolioService: PortfolioService,
    private authService: AuthService,
    private priceService: PriceService
  ) {
    this.user$ = this.authService.currentUser$;
    this.initializeForm();
  }

  private initializeForm(): void {
    this.buyForm = this.fb.group({
      symbol: ['', [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(5),
        this.symbolValidator
      ]],
      shares: ['', [
        Validators.required,
        Validators.min(1),
        Validators.pattern(/^[1-9]\d*$/)
      ]],
      pricePerShare: ['', [
        Validators.required,
        Validators.min(0.01)
      ]],
      date: [this.formatDateForInput(new Date()), [
        Validators.required,
        this.futureDateValidator
      ]]
    });

    // Écoute les changements de symbole pour mettre à jour le prix
    this.buyForm.get('symbol')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(symbol => {
        if (symbol && symbol.length >= 3) {
          this.updateStockPrice(symbol.toUpperCase());
        }
      });

    // Écoute les changements de nombre de parts pour recalculer le coût total
    this.buyForm.get('shares')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.calculateTotalCost();
      });

    // Écoute les changements de prix pour recalculer le coût total
    this.buyForm.get('pricePerShare')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.calculateTotalCost();
      });
  }

  ngOnInit(): void {
    // Charge les symboles d'actions disponibles
    this.availableSymbols = this.priceService.getAvailableSymbols();
    this.availableSymbols = this.availableSymbols.filter(symbol => symbol !== 'SPX500'); // Exclut SPX500

    // Écoute les changements utilisateur pour réinitialiser les messages
    this.user$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(user => {
      if (user) {
        this.successMessage = '';
        this.errorMessage = '';
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // Validateurs personnalisés
  private symbolValidator(control: AbstractControl): { [key: string]: any } | null {
    const value = control.value;
    if (!value) return null;

    // Vérifie que le symbole est en majuscules et ne contient que des lettres
    if (!/^[A-Z]{3,5}$/.test(value)) {
      return { invalidSymbol: true };
    }
    return null;
  }

  private futureDateValidator(control: AbstractControl): { [key: string]: any } | null {
    const value = control.value;
    if (!value) return null;

    const selectedDate = new Date(value);
    const today = new Date();
    today.setHours(23, 59, 59, 999); // Fin de journée

    if (selectedDate > today) {
      return { futureDate: true };
    }
    return null;
  }

  // Met à jour le prix de l'action sélectionnée
  private updateStockPrice(symbol: string): void {
    this.priceService.getStockPrice(symbol).pipe(
      takeUntil(this.destroy$)
    ).subscribe(price => {
      if (price) {
        this.currentPrice = price.price;
        this.priceChange = price.change;
        this.priceChangePercent = price.changePercent;
        this.buyForm.patchValue({ pricePerShare: price.price }, { emitEvent: false });
      } else {
        this.currentPrice = 0;
        this.priceChange = 0;
        this.priceChangePercent = 0;
      }
    });
  }

  // Calcule le coût total
  private calculateTotalCost(): void {
    const shares = this.buyForm.get('shares')?.value || 0;
    const pricePerShare = this.buyForm.get('pricePerShare')?.value || 0;
    const totalCost = shares * pricePerShare;
    // On peut stocker cela dans une propriété si nécessaire
  }

  // Soumission du formulaire
  onSubmit(): void {
    if (this.buyForm.invalid) {
      this.markFormGroupTouched(this.buyForm);
      return;
    }

    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';

    const formData: BuyFormData = {
      symbol: this.buyForm.value.symbol.toUpperCase(),
      shares: parseInt(this.buyForm.value.shares),
      pricePerShare: parseFloat(this.buyForm.value.pricePerShare),
      totalCost: parseInt(this.buyForm.value.shares) * parseFloat(this.buyForm.value.pricePerShare),
      date: new Date(this.buyForm.value.date)
    };

    // Vérifie le budget disponible
    const user = this.authService.currentUser;
    if (!user || formData.totalCost > user.currentBudget) {
      this.errorMessage = 'Solde insuffisant pour cet achat.';
      this.isSubmitting = false;
      return;
    }

    // Exécute l'achat
    this.portfolioService.buyStock(
      formData.symbol,
      formData.shares,
      formData.pricePerShare
    ).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (success) => {
        this.isSubmitting = false;
        if (success) {
          this.successMessage = `Achat de ${formData.shares} actions ${formData.symbol} réussi pour ${this.formatCurrency(formData.totalCost)}.`;
          this.buyForm.reset({
            symbol: '',
            shares: '',
            pricePerShare: '',
            date: this.formatDateForInput(new Date())
          });
          this.currentPrice = 0;
          this.priceChange = 0;
          this.priceChangePercent = 0;
        } else {
          this.errorMessage = 'Erreur lors de l\'achat. Veuillez réessayer.';
        }
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = 'Erreur lors de l\'achat: ' + (error.message || 'Erreur inconnue');
        console.error('Buy stock error:', error);
      }
    });
  }

  // Marque tous les champs du formulaire comme "touchés" pour afficher les erreurs
  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();

      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }

  // Utilitaires pour l'affichage
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }

  formatPercentage(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100);
  }

  // Helpers pour les templates
  getFieldError(fieldName: string): string {
    const control = this.buyForm.get(fieldName);
    if (!control || !control.touched || !control.errors) {
      return '';
    }

    if (control.errors['required']) {
      return 'Ce champ est obligatoire';
    }

    if (control.errors['minlength']) {
      return `Minimum ${control.errors['minlength'].requiredLength} caractères`;
    }

    if (control.errors['maxlength']) {
      return `Maximum ${control.errors['maxlength'].requiredLength} caractères`;
    }

    if (control.errors['min']) {
      return `Valeur minimale: ${control.errors['min'].min}`;
    }

    if (control.errors['pattern']) {
      return 'Format invalide';
    }

    if (control.errors['invalidSymbol']) {
      return 'Le symbole doit être en majuscules (3-5 caractères)';
    }

    if (control.errors['futureDate']) {
      return 'La date ne peut pas être dans le futur';
    }

    return 'Champ invalide';
  }

  getChangeClass(value: number): string {
    if (value > 0) return 'text-success';
    if (value < 0) return 'text-danger';
    return 'text-secondary';
  }

  // Actions
  refreshPrices(): void {
    this.priceService.refreshPrices().subscribe({
      next: () => {
        const symbol = this.buyForm.get('symbol')?.value;
        if (symbol) {
          this.updateStockPrice(symbol.toUpperCase());
        }
      },
      error: (error) => {
        console.error('Erreur lors de la mise à jour des prix:', error);
      }
    });
  }

  resetForm(): void {
    this.buyForm.reset({
      symbol: '',
      shares: '',
      pricePerShare: '',
      date: this.formatDateForInput(new Date())
    });
    this.currentPrice = 0;
    this.priceChange = 0;
    this.priceChangePercent = 0;
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
