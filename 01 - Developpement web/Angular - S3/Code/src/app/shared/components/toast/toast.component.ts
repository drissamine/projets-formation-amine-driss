import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService, ToastMessage } from '../../services/notification.service';
import { Observable } from 'rxjs';
import { animate, style, transition, trigger } from '@angular/animations';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-container">
      <div *ngFor="let toast of toasts$ | async" 
           class="toast-item" 
           [ngClass]="toast.type"
           [@toastAnimation]>
        <div class="toast-icon">
          <i class="fas" [ngClass]="getIcon(toast.type)"></i>
        </div>
        <div class="toast-content">
          <p>{{ toast.message }}</p>
        </div>
        <button class="toast-close" (click)="close(toast.id)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .toast-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }

    .toast-item {
      pointer-events: auto;
      min-width: 300px;
      max-width: 400px;
      background: var(--bg-surface, #ffffff);
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.1);
      display: flex;
      align-items: center;
      padding: 1rem;
      gap: 1rem;
      color: var(--text-primary, #1f2937);
      border-left: 4px solid transparent;
      backdrop-filter: blur(10px);
      
      &.success {
        border-left-color: var(--success-500, #22c55e);
        .toast-icon { color: var(--success-500, #22c55e); background: rgba(34, 197, 94, 0.1); }
      }
      
      &.error {
        border-left-color: var(--danger-500, #ef4444);
        .toast-icon { color: var(--danger-500, #ef4444); background: rgba(239, 68, 68, 0.1); }
      }
      
      &.warning {
        border-left-color: var(--warning-500, #eab308);
        .toast-icon { color: var(--warning-500, #eab308); background: rgba(234, 179, 8, 0.1); }
      }
      
      &.info {
        border-left-color: var(--info-500, #3b82f6);
        .toast-icon { color: var(--info-500, #3b82f6); background: rgba(59, 130, 246, 0.1); }
      }
    }

    .toast-icon {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      flex-shrink: 0;
    }

    .toast-content {
      flex: 1;
      p {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.4;
        font-weight: 500;
        color: var(--text-primary, #333);
      }
    }

    .toast-close {
      background: transparent;
      border: none;
      color: var(--text-secondary, #9ca3af);
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      transition: all 0.2s;
      
      &:hover {
        background: rgba(0,0,0,0.05);
        color: var(--text-primary, #333);
      }
    }

    /* Dark mode support fallback */
    @media (prefers-color-scheme: dark) {
      .toast-item {
        background: #1f2937;
        color: #f3f4f6;
        .toast-content p { color: #f3f4f6; }
      }
    }
  `],
  animations: [
    trigger('toastAnimation', [
      transition(':enter', [
        style({ transform: 'translateX(100%)', opacity: 0 }),
        animate('300ms cubic-bezier(0.25, 0.8, 0.25, 1)', style({ transform: 'translateX(0)', opacity: 1 }))
      ]),
      transition(':leave', [
        animate('300ms cubic-bezier(0.25, 0.8, 0.25, 1)', style({ transform: 'translateX(100%)', opacity: 0 }))
      ])
    ])
  ]
})
export class Toast {
  toasts$: Observable<ToastMessage[]>;

  constructor(private notificationService: NotificationService) {
    this.toasts$ = this.notificationService.toasts$;
  }

  close(id: string): void {
    this.notificationService.remove(id);
  }

  getIcon(type: string): string {
    switch (type) {
      case 'success': return 'fa-check';
      case 'error': return 'fa-exclamation-circle';
      case 'warning': return 'fa-exclamation-triangle';
      default: return 'fa-info-circle';
    }
  }
}
