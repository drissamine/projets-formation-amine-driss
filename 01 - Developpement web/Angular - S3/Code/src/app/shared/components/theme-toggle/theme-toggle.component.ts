import { Component } from '@angular/core';
import { ThemeService } from '../../services/theme.service';

/**
 * Modern Theme Toggle Component
 * Provides a sleek button to toggle between light and dark themes
 */
@Component({
  selector: 'app-theme-toggle',
  templateUrl: './theme-toggle.component.html',
  styleUrls: ['./theme-toggle.component.scss']
})
export class ThemeToggleComponent {
  constructor(public themeService: ThemeService) { }

  /**
   * Toggle theme with smooth transition
   */
  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  /**
   * Set specific theme
   */
  setTheme(theme: 'light' | 'dark'): void {
    this.themeService.setTheme(theme);
  }
}
