import { Injectable, signal, computed, effect } from '@angular/core';

export type Theme = 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  // Signal réactif pour le thème actuel
  private _currentTheme = signal<Theme>('light');
  currentTheme = this._currentTheme.asReadonly();

  // Signal calculé pour vérifier si c'est le mode sombre
  isDarkMode = computed(() => this._currentTheme() === 'dark');

  constructor() {
    // Charger le thème sauvegardé ou détecter la préférence système
    this.loadTheme();

    // Effet pour synchroniser le DOM avec le signal
    effect(() => {
      const theme = this._currentTheme();
      this.applyTheme(theme);
    });
  }

  /**
   * Bascule entre les thèmes clair et sombre
   */
  toggleTheme(): void {
    const newTheme: Theme = this._currentTheme() === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  /**
   * Définit un thème spécifique
   */
  setTheme(theme: Theme): void {
    this._currentTheme.set(theme);
  }

  /**
   * Active le mode sombre
   */
  enableDarkMode(): void {
    this.setTheme('dark');
  }

  /**
   * Active le mode clair
   */
  enableLightMode(): void {
    this.setTheme('light');
  }

  /**
   * Utilise la préférence système
   */
  useSystemPreference(): void {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.setTheme(prefersDark ? 'dark' : 'light');
  }

  /**
   * Écoute les changements de préférence système
   */
  listenToSystemChanges(): void {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (event) => {
      if (localStorage.getItem('portfolio-theme-preference') === 'system') {
        this.setTheme(event.matches ? 'dark' : 'light');
      }
    });
  }

  /**
   * Retourne le thème actuel
   */
  getCurrentTheme(): Theme {
    return this._currentTheme();
  }

  /**
   * Vérifie si le mode sombre est actif
   */
  isDark(): boolean {
    return this.isDarkMode();
  }

  /**
   * Charge le thème depuis localStorage ou utilise la préférence système
   */
  private loadTheme(): void {
    const saved = localStorage.getItem('portfolio-theme-preference');

    if (saved === 'light' || saved === 'dark') {
      this._currentTheme.set(saved as Theme);
    } else if (saved === 'system') {
      this.useSystemPreference();
    } else {
      // Première visite : utiliser la préférence système
      this.useSystemPreference();
    }

    // Écouter les changements système
    this.listenToSystemChanges();
  }

  /**
   * Applique le thème au DOM
   */
  private applyTheme(theme: Theme): void {
    // Appliquer l'attribut data-theme sur l'élément html
    document.documentElement.setAttribute('data-theme', theme);

    // Sauvegarder la préférence
    localStorage.setItem('portfolio-theme-preference', theme);

    // Ajouter une classe de transition pour les animations fluides
    document.documentElement.classList.add('theme-transitioning');
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning');
    }, 500);
  }
}
