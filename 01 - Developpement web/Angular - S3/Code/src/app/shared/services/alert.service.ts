import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { PortfolioAlert, AlertType } from '../models/portfolio.model';
import { PriceService } from './price.service';
import { PortfolioService } from './portfolio.service';
import { AuthService } from './auth.service';

import { NotificationService } from './notification.service';

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private readonly STORAGE_KEY = 'portfolio_alerts';

  // État des alertes
  private alertsSubject = new BehaviorSubject<PortfolioAlert[]>([]);
  public alerts$ = this.alertsSubject.asObservable();

  constructor(
    private priceService: PriceService,
    private portfolioService: PortfolioService,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {
    // Charge les alertes au démarrage
    this.loadAlerts();

    // Écoute les changements de prix pour vérifier les alertes
    this.priceService.getAllStockPrices().subscribe(() => {
      this.checkAlerts();
    });

    // Écoute les changements d'utilisateur
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.loadAlerts();
      } else {
        this.clearAlerts();
      }
    });
  }

  /**
   * Charge les alertes depuis le localStorage
   */
  private loadAlerts(): void {
    const user = this.authService.currentUser;
    if (!user) return;

    const alertsJson = localStorage.getItem(`${this.STORAGE_KEY}_${user.id}`);
    const alerts: PortfolioAlert[] = alertsJson
      ? JSON.parse(alertsJson).map((a: any) => ({
        ...a,
        createdAt: new Date(a.createdAt),
        triggeredAt: a.triggeredAt ? new Date(a.triggeredAt) : undefined
      }))
      : [];

    this.alertsSubject.next(alerts);
  }

  /**
   * Sauvegarde les alertes dans le localStorage
   */
  private saveAlerts(): void {
    const user = this.authService.currentUser;
    if (!user) return;

    localStorage.setItem(
      `${this.STORAGE_KEY}_${user.id}`,
      JSON.stringify(this.alertsSubject.value)
    );
  }

  /**
   * Vérifie toutes les alertes contre les prix actuels
   */
  private checkAlerts(): void {
    const alerts = this.alertsSubject.value;
    const currentPrices = this.priceService['stockPrices'].value;

    let hasChanges = false;
    const newlyTriggered: PortfolioAlert[] = [];

    const updatedAlerts = alerts.map(alert => {
      if (alert.isTriggered) return alert;

      const currentPrice = currentPrices[alert.stockSymbol];
      if (!currentPrice) return alert;

      let shouldTrigger = false;

      switch (alert.alertType) {
        case AlertType.PRICE_DROP:
          shouldTrigger = currentPrice.price <= alert.threshold;
          break;
        case AlertType.PRICE_RISE:
          shouldTrigger = currentPrice.price >= alert.threshold;
          break;
        case AlertType.GAIN_TARGET:
          // Calculer le gain par rapport au prix d'achat moyen
          const portfolio = this.portfolioService['portfolioSubject'].value;
          const stock = portfolio?.stocks.find(s => s.symbol === alert.stockSymbol);
          if (stock) {
            const gainPercent = ((currentPrice.price - stock.averageCost) / stock.averageCost) * 100;
            shouldTrigger = gainPercent >= alert.threshold;
          }
          break;
        case AlertType.LOSS_LIMIT:
          // Calculer la perte par rapport au prix d'achat moyen
          if (stock) {
            const lossPercent = ((stock.averageCost - currentPrice.price) / stock.averageCost) * 100;
            shouldTrigger = lossPercent >= alert.threshold;
          }
          break;
      }

      if (shouldTrigger) {
        hasChanges = true;
        const triggeredAlert = {
          ...alert,
          isTriggered: true,
          currentValue: currentPrice.price,
          triggeredAt: new Date(),
          message: this.generateAlertMessage(alert, currentPrice.price)
        };
        newlyTriggered.push(triggeredAlert);
        return triggeredAlert;
      }

      return {
        ...alert,
        currentValue: currentPrice.price
      };
    });

    if (hasChanges) {
      this.alertsSubject.next(updatedAlerts);
      this.saveAlerts();
      this.showNotification(newlyTriggered);
    }
  }

  /**
   * Génère le message d'alerte
   */
  private generateAlertMessage(alert: PortfolioAlert, currentPrice: number): string {
    const symbol = alert.stockSymbol;

    switch (alert.alertType) {
      case AlertType.PRICE_DROP:
        return `${symbol} a atteint ${currentPrice.toFixed(2)}€ (seuil: ${alert.threshold}€)`;
      case AlertType.PRICE_RISE:
        return `${symbol} a atteint ${currentPrice.toFixed(2)}€ (seuil: ${alert.threshold}€)`;
      case AlertType.GAIN_TARGET:
        return `${symbol} a atteint l'objectif de gain de ${alert.threshold}%`;
      case AlertType.LOSS_LIMIT:
        return `${symbol} a atteint la limite de perte de ${alert.threshold}%`;
      default:
        return `Alerte déclenchée pour ${symbol}`;
    }
  }

  /**
   * Affiche une notification
   */
  private showNotification(newAlerts: PortfolioAlert[]): void {
    if (newAlerts.length === 0) return;

    // Jouer un son
    this.playNotificationSound();

    // Afficher la notification in-app pour chaque alerte
    newAlerts.forEach(alert => {
      // Détermine le type de notification en fonction de l'alerte
      let type: 'info' | 'success' | 'warning' | 'error' = 'info';
      switch (alert.alertType) {
        case AlertType.GAIN_TARGET: type = 'success'; break;
        case AlertType.LOSS_LIMIT: type = 'error'; break;
        case AlertType.PRICE_DROP: type = 'warning'; break;
        case AlertType.PRICE_RISE: type = 'info'; break;
      }

      this.notificationService.show(alert.message, type, 8000); // 8 secondes pour bien lire
    });
  }

  private playNotificationSound(): void {
    try {
      // Utilisation de l'API Web Audio pour générer un son sans dépendance externe
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContext) return;

      const ctx = new AudioContext();

      // Si le contexte est suspendu (politique auto-play), on essaie de le reprendre
      // Cela fonctionnera si l'utilisateur a déjà interagit avec la page
      if (ctx.state === 'suspended') {
        ctx.resume().catch(() => { });
      }

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      // Configuration d'un son type "Ding" (Sinusoidale avec envelope)
      // C5 (523.25Hz) -> C6(1046.5Hz) transition rapide
      osc.type = 'sine';
      osc.frequency.setValueAtTime(523.25, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.1);

      // Envelope de volume (Attaque rapide, décroissance douce)
      gain.gain.setValueAtTime(0, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);

      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.5);

    } catch (e) {
      console.warn('Impossible de jouer le son de notification via Web Audio API', e);
    }
  }

  /**
   * Crée une nouvelle alerte
   */
  createAlert(
    stockSymbol: string,
    alertType: AlertType,
    threshold: number,
    customMessage?: string
  ): Observable<boolean> {
    return new Observable(observer => {
      const user = this.authService.currentUser;
      if (!user) {
        observer.next(false);
        observer.complete();
        return;
      }

      // Vérifie si une alerte similaire existe déjà
      const existingAlert = this.alertsSubject.value.find(
        a => a.stockSymbol === stockSymbol &&
          a.alertType === alertType &&
          a.threshold === threshold &&
          !a.isTriggered
      );

      if (existingAlert) {
        observer.next(false);
        observer.complete();
        return;
      }

      const alert: PortfolioAlert = {
        id: this.generateId(),
        userId: user.id,
        stockSymbol: stockSymbol.toUpperCase(),
        alertType,
        threshold,
        currentValue: 0,
        isTriggered: false,
        message: customMessage || this.generateAlertMessage({
          id: '',
          userId: user.id,
          stockSymbol,
          alertType,
          threshold,
          currentValue: 0,
          isTriggered: false,
          message: '',
          createdAt: new Date()
        }, 0),
        createdAt: new Date()
      };

      const currentAlerts = this.alertsSubject.value;
      this.alertsSubject.next([...currentAlerts, alert]);
      this.saveAlerts();

      observer.next(true);
      observer.complete();
    });
  }

  /**
   * Supprime une alerte
   */
  deleteAlert(alertId: string): void {
    const alerts = this.alertsSubject.value.filter(alert => alert.id !== alertId);
    this.alertsSubject.next(alerts);
    this.saveAlerts();
  }

  /**
   * Marque une alerte comme lue
   */
  markAsRead(alertId: string): void {
    const alerts = this.alertsSubject.value.map(alert =>
      alert.id === alertId ? { ...alert, isTriggered: true } : alert
    );
    this.alertsSubject.next(alerts);
    this.saveAlerts();
  }

  /**
   * Obtient les alertes actives (non déclenchées)
   */
  getActiveAlerts(): Observable<PortfolioAlert[]> {
    return this.alerts$.pipe(
      map(alerts => alerts.filter(alert => !alert.isTriggered))
    );
  }

  /**
   * Obtient les alertes déclenchées
   */
  getTriggeredAlerts(): Observable<PortfolioAlert[]> {
    return this.alerts$.pipe(
      map(alerts => alerts.filter(alert => alert.isTriggered))
    );
  }

  /**
   * Demande la permission de notification
   */
  requestNotificationPermission(): void {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  /**
   * Génère un ID unique
   */
  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Efface toutes les alertes
   */
  private clearAlerts(): void {
    this.alertsSubject.next([]);
  }

  /**
   * Obtient les alertes pour un symbole spécifique
   */
  getAlertsForSymbol(symbol: string): Observable<PortfolioAlert[]> {
    return this.alerts$.pipe(
      map(alerts => alerts.filter(alert => alert.stockSymbol === symbol.toUpperCase()))
    );
  }

  /**
   * Efface les alertes déclenchées anciennes
   */
  clearOldTriggeredAlerts(daysOld: number = 30): void {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysOld);

    const alerts = this.alertsSubject.value.filter(alert =>
      !alert.isTriggered || (alert.triggeredAt && alert.triggeredAt > cutoffDate)
    );

    this.alertsSubject.next(alerts);
    this.saveAlerts();
  }
}
