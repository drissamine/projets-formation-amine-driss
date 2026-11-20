import { TestBed } from '@angular/core/testing';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  let service: ThemeService;

  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      clear: vi.fn(),
      removeItem: vi.fn(),
      length: 0,
      key: vi.fn(),
    };
    (globalThis as any).localStorage = localStorageMock;

    // Mock window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    TestBed.configureTestingModule({
      providers: [ThemeService]
    });
  });

  it('should be created', () => {
    service = TestBed.inject(ThemeService);
    expect(service).toBeTruthy();
  });

  it('should initialize with light theme by default when no localStorage value', () => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    service = TestBed.inject(ThemeService);

    expect(service.getCurrentTheme()).toBe('light');
    expect(service.isDark()).toBe(false);
  });

  it('should initialize with saved theme from localStorage', () => {
    vi.mocked(localStorage.getItem).mockReturnValue('dark');
    service = TestBed.inject(ThemeService);

    expect(service.getCurrentTheme()).toBe('dark');
    expect(service.isDark()).toBe(true);
  });

  it('should toggle theme from light to dark', () => {
    vi.mocked(localStorage.getItem).mockReturnValue('light');
    service = TestBed.inject(ThemeService);

    service.toggleTheme();

    expect(service.getCurrentTheme()).toBe('dark');
    expect(service.isDark()).toBe(true);
    expect(localStorage.setItem).toHaveBeenCalledWith('portfolio-theme-preference', 'dark');
  });

  it('should toggle theme from dark to light', () => {
    vi.mocked(localStorage.getItem).mockReturnValue('dark');
    service = TestBed.inject(ThemeService);

    service.toggleTheme();

    expect(service.getCurrentTheme()).toBe('light');
    expect(service.isDark()).toBe(false);
    expect(localStorage.setItem).toHaveBeenCalledWith('portfolio-theme-preference', 'light');
  });

  it('should enable dark mode', () => {
    vi.mocked(localStorage.getItem).mockReturnValue('light');
    service = TestBed.inject(ThemeService);

    service.enableDarkMode();

    expect(service.getCurrentTheme()).toBe('dark');
    expect(service.isDark()).toBe(true);
  });

  it('should enable light mode', () => {
    vi.mocked(localStorage.getItem).mockReturnValue('dark');
    service = TestBed.inject(ThemeService);

    service.enableLightMode();

    expect(service.getCurrentTheme()).toBe('light');
    expect(service.isDark()).toBe(false);
  });

  it('should use system preference when method is called', () => {
    // Mock system prefers dark
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    service = TestBed.inject(ThemeService);
    service.useSystemPreference();

    expect(service.getCurrentTheme()).toBe('dark');
  });

  it('should handle localStorage errors gracefully', () => {
    vi.mocked(localStorage.getItem).mockImplementation(() => {
      throw new Error('localStorage is not available');
    });

    // Should not throw and default to light theme
    expect(() => {
      service = TestBed.inject(ThemeService);
    }).not.toThrow();

    expect(service.getCurrentTheme()).toBe('light');
  });

  it('should set theme attribute on document element', () => {
    service = TestBed.inject(ThemeService);

    service.setTheme('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

    service.setTheme('light');
    expect(document.documentElement.getAttribute('data-theme')).toBeNull();
  });
});