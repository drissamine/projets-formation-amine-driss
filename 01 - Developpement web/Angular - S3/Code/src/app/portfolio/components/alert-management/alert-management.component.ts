import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Observable, Subject } from 'rxjs';
import { map, takeUntil } from 'rxjs/operators';
import { PortfolioAlert, AlertType } from '../../../shared/models/portfolio.model';
import { AlertService } from '../../../shared/services/alert.service';
import { PortfolioService } from '../../../shared/services/portfolio.service';
import { PriceService } from '../../../shared/services/price.service';

@Component({
  selector: 'app-alert-management',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './alert-management.component.html',
  styleUrls: ['./alert-management.component.scss']
})
export class AlertManagementComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  alertForm: FormGroup;
  activeAlerts$: Observable<PortfolioAlert[]>;
  triggeredAlerts$: Observable<PortfolioAlert[]>;
  availableSymbols: string[] = [];
  alertTypes = Object.values(AlertType);

  isSubmitting = false;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private alertService: AlertService,
    private portfolioService: PortfolioService,
    private priceService: PriceService
  ) {
    this.activeAlerts$ = this.alertService.getActiveAlerts();
    this.triggeredAlerts$ = this.alertService.getTriggeredAlerts();

    this.alertForm = this.fb.group({
      stockSymbol: ['', [Validators.required, Validators.pattern(/^[A-Z]{3,5}$/)]],
      alertType: [AlertType.PRICE_DROP, Validators.required],
      threshold: ['', [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    this.alertService.requestNotificationPermission();
    this.availableSymbols = this.priceService.getAvailableSymbols();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onSubmit(): void {
    if (this.alertForm.invalid) return;

    this.isSubmitting = true;
    this.successMessage = '';
    this.errorMessage = '';

    const { stockSymbol, alertType, threshold } = this.alertForm.value;

    this.alertService.createAlert(
      stockSymbol.toUpperCase(),
      alertType,
      parseFloat(threshold)
    ).pipe(
      takeUntil(this.destroy$)
    ).subscribe(success => {
      this.isSubmitting = false;
      if (success) {
        this.successMessage = 'Alerte créée avec succès';
        this.alertForm.reset({ alertType: AlertType.PRICE_DROP });
      } else {
        this.errorMessage = 'Erreur lors de la création de l\'alerte (doublon possible)';
      }
    });
  }

  deleteAlert(alertId: string): void {
    this.alertService.deleteAlert(alertId);
  }

  markAsRead(alertId: string): void {
    this.alertService.markAsRead(alertId);
  }

  getLabelForAlertType(type: AlertType): string {
    switch (type) {
      case AlertType.PRICE_DROP: return 'Prix inférieur à';
      case AlertType.PRICE_RISE: return 'Prix supérieur à';
      case AlertType.GAIN_TARGET: return 'Gain supérieur à (%)';
      case AlertType.LOSS_LIMIT: return 'Perte supérieure à (%)';
      default: return type;
    }
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }

  formatDate(date: Date): string {
    if (!date) return '-';
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
    }).format(new Date(date));
  }
}
