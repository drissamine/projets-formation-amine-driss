import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ToastMessage {
    id: string;
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
    duration?: number;
}

@Injectable({
    providedIn: 'root'
})
export class NotificationService {
    private toastsSubject = new BehaviorSubject<ToastMessage[]>([]);
    public toasts$ = this.toastsSubject.asObservable();

    constructor() { }

    show(message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info', duration: number = 5000): void {
        const id = Date.now().toString(36) + Math.random().toString(36).substr(2);
        const toast: ToastMessage = { id, message, type, duration };

        const currentToasts = this.toastsSubject.value;
        this.toastsSubject.next([...currentToasts, toast]);

        if (duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }
    }

    success(message: string, duration?: number): void {
        this.show(message, 'success', duration);
    }

    error(message: string, duration?: number): void {
        this.show(message, 'error', duration);
    }

    info(message: string, duration?: number): void {
        this.show(message, 'info', duration);
    }

    warning(message: string, duration?: number): void {
        this.show(message, 'warning', duration);
    }

    remove(id: string): void {
        const currentToasts = this.toastsSubject.value;
        this.toastsSubject.next(currentToasts.filter(t => t.id !== id));
    }
}
