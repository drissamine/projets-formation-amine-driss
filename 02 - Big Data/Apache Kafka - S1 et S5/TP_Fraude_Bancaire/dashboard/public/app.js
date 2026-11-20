// Créé par DRISS Amine
// Application Dashboard Détection Fraude
class FraudDashboard {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.alertCounters = {
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0
    };
    this.lastAlerts = [];
    this.lastTimestamp = null;

    // Paramètres des notifications
    this.notificationsEnabled = localStorage.getItem('notificationsEnabled') === 'true';
    this.soundEnabled = localStorage.getItem('soundEnabled') !== 'false'; // true par défaut
    this.toastEnabled = localStorage.getItem('toastEnabled') !== 'false'; // true par défaut

    this.init();
  }

  init() {
    this.connectWebSocket();
    this.setupEventListeners();
    this.setupUIControls();
  }

  connectWebSocket() {
    this.socket = io();

    this.socket.on('connect', () => {
      console.log('Connecté au serveur WebSocket');
      this.setConnectionStatus(true);
    });

    this.socket.on('disconnect', () => {
      console.log('Déconnecté du serveur WebSocket');
      this.setConnectionStatus(false);
    });

    this.socket.on('initialState', (data) => {
      console.log('État initial reçu:', data);
      this.updateDashboard(data);
    });

    this.socket.on('alertUpdate', (data) => {
      console.log('Mise à jour d\'alerte reçue:', data);

      // Définir le timestamp de réception côté client
      const receivedAt = new Date().toISOString();

      // Ajouter receivedAt aux alertes
      if (data.lastAlerts) {
        data.lastAlerts = data.lastAlerts.map(alert => ({
          ...alert,
          receivedAt: alert.receivedAt || receivedAt
        }));
      }

      // Ajouter receivedAt à la nouvelle alerte
      if (data.newAlert) {
        data.newAlert.receivedAt = receivedAt;
      }

      this.updateDashboard(data);

      // Notifications pour la nouvelle alerte
      if (data.newAlert) {
        this.handleNewAlert(data.newAlert);
      }

      // Attacher les event listeners pour les nouveaux boutons toggle
      this.attachToggleListeners();
    });


  }

  setupEventListeners() {
    // Reconnexion automatique en cas de perte de connexion
    this.socket.on('connect_error', (error) => {
      console.error('Erreur de connexion WebSocket:', error);
      this.setConnectionStatus(false);
    });
  }

  setConnectionStatus(connected) {
    this.isConnected = connected;
    const statusDot = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-text');

    if (connected) {
      statusDot.className = 'status-dot connected';
      statusText.textContent = 'Connecté';
    } else {
      statusDot.className = 'status-dot disconnected';
      statusText.textContent = 'Déconnecté - Tentative de reconnexion...';
    }
  }

  updateDashboard(data) {
    // Mettre à jour les compteurs
    if (data.counters) {
      this.updateCounters(data.counters);
    }

    // Mettre à jour les dernières alertes
    if (data.lastAlerts) {
      this.updateAlertsList(data.lastAlerts);
    }

    // Mettre à jour le timestamp de dernière alerte
    if (data.lastTimestamp) {
      this.updateLastTimestamp(data.lastTimestamp);
    }
  }

  updateCounters(counters) {
    this.alertCounters = counters;

    // Mettre à jour chaque compteur avec animation
    Object.keys(counters).forEach(severity => {
      const element = document.getElementById(`${severity.toLowerCase()}-counter`);
      if (element) {
        const currentValue = parseInt(element.textContent);
        const newValue = counters[severity];

        element.textContent = newValue;

        // Animation si la valeur a changé
        if (currentValue !== newValue) {
          element.classList.add('updated');
          setTimeout(() => element.classList.remove('updated'), 500);
        }
      }
    });
  }

  updateAlertsList(alerts) {
    this.lastAlerts = alerts;
    const alertsList = document.getElementById('alerts-list');

    if (alerts.length === 0) {
      alertsList.innerHTML = '<div class="no-alerts"><p>En attente d\'alertes...</p></div>';
      return;
    }

    alertsList.innerHTML = '';

    alerts.forEach((alert, index) => {
      const alertElement = this.createAlertElement(alert, index === 0);
      alertsList.appendChild(alertElement);
    });
  }

  createAlertElement(alert, isNew = false) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item ${alert.severity.toLowerCase()}${isNew ? ' new-alert' : ''}`;

    const timestamp = this.formatTimestampWithTimezone(alert.timestamp, 'Europe/Paris');
    const receivedAt = alert.receivedAt ? this.formatTimestampWithTimezone(alert.receivedAt, 'Europe/Paris') : timestamp;

    // Score de risque avec couleur
    const riskScoreClass = alert.risk_score >= 80 ? 'high' :
                          alert.risk_score >= 60 ? 'medium' : 'low';

    alertDiv.innerHTML = `
      <div class="alert-header">
        <div>
          <span class="alert-rule">${this.formatRuleName(alert.rule)}</span>
          ${alert.risk_score ? `<span class="risk-score ${riskScoreClass}">🎯 ${alert.risk_score}%</span>` : ''}
        </div>
        <span class="alert-severity ${alert.severity.toLowerCase()}">${alert.severity}</span>
      </div>

      ${alert.reason ? `<div class="alert-reason">💡 ${alert.reason}</div>` : ''}

      <div class="alert-details">
        <div class="alert-detail">
          <span>ID Transaction</span>
          <span>${alert.transaction_id}</span>
        </div>
        <div class="alert-detail">
          <span>Client</span>
          <span>${alert.client_id}</span>
        </div>
        <div class="alert-detail">
          <span>Timestamp</span>
          <span>${timestamp}</span>
        </div>
        <div class="alert-detail">
          <span>Reçu à</span>
          <span>${receivedAt}</span>
        </div>
      </div>

      <button class="alert-toggle">
        Voir plus ▼
      </button>

      <div class="alert-details-expanded">
        <div class="alert-details-grid">
          ${alert.amount ? `<div class="detail-item amount"><span class="detail-icon">💰</span><span class="detail-label">Montant</span><span class="detail-value">${this.formatCurrency(alert.amount, alert.currency)}</span></div>` : ''}
          ${alert.merchant ? `<div class="detail-item merchant"><span class="detail-icon">🏪</span><span class="detail-label">Marchand</span><span class="detail-value">${alert.merchant}</span></div>` : ''}
          ${alert.merchant_country ? `<div class="detail-item"><span class="detail-icon">🌍</span><span class="detail-label">Pays</span><span class="detail-value">${alert.merchant_country}</span></div>` : ''}
          ${alert.channel ? `<div class="detail-item"><span class="detail-icon">📱</span><span class="detail-label">Canal</span><span class="detail-value">${this.formatChannel(alert.channel)}</span></div>` : ''}
          ${alert.type ? `<div class="detail-item"><span class="detail-icon">💳</span><span class="detail-label">Type</span><span class="detail-value">${this.formatType(alert.type)}</span></div>` : ''}
          ${alert.ip_address ? `<div class="detail-item ip"><span class="detail-icon">🌐</span><span class="detail-label">Adresse IP</span><span class="detail-value">${alert.ip_address}</span></div>` : ''}
          ${alert.time_since_last_transaction ? `<div class="detail-item time-since"><span class="detail-icon">⏱️</span><span class="detail-label">Dernière TX</span><span class="detail-value">${alert.time_since_last_transaction}</span></div>` : ''}
        </div>
      </div>
    `;

    // Masquer les détails par défaut
    const detailsElement = alertDiv.querySelector('.alert-details-expanded');
    if (detailsElement) {
      detailsElement.classList.add('alert-details-collapsed');
    }

    return alertDiv;
  }

  formatRuleName(rule) {
    const ruleNames = {
      'MONTANT_ELEVE': 'Montant Élevé',
      'PAYS_RISQUE': 'Pays à Risque',
      'TRANSACTIONS_RAPIDES': 'Transactions Rapides',
      'HEURE_INHABITUELLE': 'Heure Inhabituelle',
      'NOUVEAU_MARCHAND': 'Nouveau Marchand'
    };
    return ruleNames[rule] || rule;
  }

  formatCurrency(amount, currency) {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency || 'EUR'
    }).format(amount);
  }

  formatChannel(channel) {
    const channels = {
      'WEB': '🌐 Web',
      'MOBILE': '📱 Mobile',
      'TERMINAL': '💻 Terminal'
    };
    return channels[channel] || channel;
  }

  formatType(type) {
    const types = {
      'CARTE': '💳 Carte',
      'VIREMENT': '🏦 Virement',
      'PRELEVEMENT': '📄 Prélèvement'
    };
    return types[type] || type;
  }

  formatTimestampWithTimezone(timestamp, timezone) {
    const date = new Date(timestamp);
    const options = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: timezone
    };

    const formatted = new Intl.DateTimeFormat('fr-FR', options).format(date);
    const timezoneLabel = timezone === 'UTC' ? 'UTC' : 'Paris';
    return `${formatted} (${timezoneLabel})`;
  }

  updateLastTimestamp(timestamp) {
    this.lastTimestamp = timestamp;
    const element = document.getElementById('last-timestamp');

    if (timestamp) {
      const formatted = new Date(timestamp).toLocaleString('fr-FR');
      element.textContent = formatted;
    } else {
      element.textContent = 'Aucune';
    }
  }



  setupUIControls() {
    // Bouton notifications
    const notificationToggle = document.getElementById('notification-toggle');
    if (notificationToggle) {
      this.updateNotificationButton();
      notificationToggle.addEventListener('click', () => {
        this.toggleNotifications();
      });
    }

    // Bouton rafraîchir
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.refreshDashboard();
      });
    }

    // Délégation d'événements pour les boutons toggle d'alertes
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('alert-toggle')) {
        this.handleAlertToggle(e.target);
      }
    });

    // Raccourci pour rafraîchir (F5 ou Ctrl/Cmd + R)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'F5' || ((e.ctrlKey || e.metaKey) && e.key === 'r')) {
        e.preventDefault();
        this.refreshDashboard();
      }
    });
  }

  updateNotificationButton() {
    const notificationToggle = document.getElementById('notification-toggle');
    if (notificationToggle) {
      if (this.notificationsEnabled) {
        notificationToggle.classList.add('enabled');
        notificationToggle.querySelector('.notification-icon').textContent = '🔔';
      } else {
        notificationToggle.classList.remove('enabled');
        notificationToggle.querySelector('.notification-icon').textContent = '🔕';
      }
    }
  }

  async toggleNotifications() {
    if (!this.notificationsEnabled) {
      // Demander la permission pour les notifications push
      const permission = await this.requestNotificationPermission();
      if (permission === 'granted') {
        this.notificationsEnabled = true;
        localStorage.setItem('notificationsEnabled', 'true');
        this.showToast('Notifications activées', 'success');
      } else {
        this.showToast('Permission refusée pour les notifications', 'warning');
        return;
      }
    } else {
      this.notificationsEnabled = false;
      localStorage.setItem('notificationsEnabled', 'false');
      this.showToast('Notifications désactivées', 'info');
    }

    this.updateNotificationButton();
  }

  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      console.warn('Ce navigateur ne supporte pas les notifications');
      return 'denied';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission === 'denied') {
      return 'denied';
    }

    const permission = await Notification.requestPermission();
    return permission;
  }

  showBrowserNotification(alert) {
    if (!this.notificationsEnabled || Notification.permission !== 'granted') {
      return;
    }

    const title = this.getNotificationTitle(alert);
    const options = {
      body: `Transaction ${alert.transaction_id} - Règle: ${alert.rule}`,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: `fraud-alert-${alert.transaction_id}`,
      requireInteraction: alert.severity === 'HIGH',
      silent: false
    };

    const notification = new Notification(title, options);

    // Auto-fermeture après 5 secondes (sauf HIGH)
    if (alert.severity !== 'HIGH') {
      setTimeout(() => notification.close(), 5000);
    }

    // Gestion du clic
    notification.onclick = () => {
      window.focus();
      notification.close();
    };
  }

  getNotificationTitle(alert) {
    const severityEmojis = {
      HIGH: '🚨',
      MEDIUM: '⚠️',
      LOW: 'ℹ️'
    };

    const severityLabels = {
      HIGH: 'CRITIQUE',
      MEDIUM: 'IMPORTANT',
      LOW: 'INFORMATION'
    };

    return `${severityEmojis[alert.severity]} Alerte ${severityLabels[alert.severity]} - Fraude Détectée`;
  }

  showToast(message, type = 'info', duration = 4000) {
    if (!this.toastEnabled) return;

    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
      <div class="toast-header">
        <span class="toast-title">${this.getToastTitle(type)}</span>
        <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
      <div class="toast-message">${message}</div>
    `;

    toastContainer.appendChild(toast);

    // Animation d'entrée
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto-suppression
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, duration);

    // Limiter à 3 toasts maximum
    const toasts = toastContainer.children;
    if (toasts.length > 3) {
      toasts[0].remove();
    }
  }

  getToastTitle(type) {
    const titles = {
      success: '✅ Succès',
      error: '❌ Erreur',
      warning: '⚠️ Avertissement',
      info: 'ℹ️ Information'
    };
    return titles[type] || titles.info;
  }

  playNotificationSound(severity) {
    if (!this.soundEnabled) return;

    // Créer un contexte audio pour jouer un son
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      // Configuration selon la sévérité
      const frequencies = { HIGH: 800, MEDIUM: 600, LOW: 400 };
      const durations = { HIGH: 0.5, MEDIUM: 0.3, LOW: 0.2 };

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.setValueAtTime(frequencies[severity], audioContext.currentTime);
      oscillator.type = 'sine';

      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + durations[severity]);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + durations[severity]);
    } catch (error) {
      console.warn('Impossible de jouer le son de notification:', error);
    }
  }

  refreshDashboard() {
    // Animation de chargement
    const refreshBtn = document.getElementById('refresh-btn');
    const originalIcon = refreshBtn.querySelector('.refresh-icon').textContent;

    refreshBtn.querySelector('.refresh-icon').textContent = '⏳';
    refreshBtn.disabled = true;

    // Simuler un rafraîchissement (en réalité, les données arrivent via WebSocket)
    setTimeout(() => {
      refreshBtn.querySelector('.refresh-icon').textContent = originalIcon;
      refreshBtn.disabled = false;

      // Animation de succès
      refreshBtn.style.transform = 'scale(1.1)';
      setTimeout(() => {
        refreshBtn.style.transform = 'scale(1)';
      }, 200);
    }, 1000);
  }

  handleNewAlert(alert) {
    // 1. Animation visuelle
    this.animateNewAlert();

    // 2. Notification push du navigateur
    this.showBrowserNotification(alert);

    // 3. Notification toast
    const severityLabels = {
      HIGH: 'Critique',
      MEDIUM: 'Important',
      LOW: 'Information'
    };

    this.showToast(
      `Nouvelle alerte ${severityLabels[alert.severity].toLowerCase()} détectée`,
      alert.severity.toLowerCase()
    );

    // 4. Son de notification
    this.playNotificationSound(alert.severity);

    // 5. Vibration (si supporté)
    if ('vibrate' in navigator) {
      const vibrationPattern = alert.severity === 'HIGH' ? [200, 100, 200] : [100];
      navigator.vibrate(vibrationPattern);
    }
  }

  handleAlertToggle(button) {
    console.log('Toggle button clicked via event delegation', button);

    // Trouver l'élément des détails dans le même conteneur parent
    const alertItem = button.closest('.alert-item');
    console.log('Alert item found:', alertItem);

    if (alertItem) {
      const detailsElement = alertItem.querySelector('.alert-details-expanded');
      console.log('Details element found:', detailsElement);

      if (detailsElement) {
        // Toggle la classe
        const isCollapsed = detailsElement.classList.contains('alert-details-collapsed');
        console.log('Is collapsed:', isCollapsed);

        if (isCollapsed) {
          detailsElement.classList.remove('alert-details-collapsed');
          button.textContent = 'Voir moins ▲';
          console.log('Expanded details');
        } else {
          detailsElement.classList.add('alert-details-collapsed');
          button.textContent = 'Voir plus ▼';
          console.log('Collapsed details');
        }
      } else {
        console.error('Details element not found');
      }
    } else {
      console.error('Alert item not found');
    }
  }

  animateNewAlert() {
    // Animation du titre
    const header = document.querySelector('header h1');
    header.style.animation = 'none';
    setTimeout(() => {
      header.style.animation = 'pulse 0.5s ease';
    }, 10);
  }
}

// Fonction d'initialisation
function initDashboard() {
  console.log('Initialisation du dashboard...');
  new FraudDashboard();
}

// Démarrer quand le DOM est chargé
document.addEventListener('DOMContentLoaded', initDashboard);

// Styles CSS supplémentaires pour les animations
const additionalStyles = `
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
`;



// Ajouter les styles supplémentaires
const style = document.createElement('style');
style.textContent = additionalStyles;
document.head.appendChild(style);
