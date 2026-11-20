import { trigger, style, animate, transition, query, stagger } from '@angular/animations';

export const fadeAnimation = trigger('fadeAnimation', [
    transition(':enter', [
        style({ opacity: 0 }),
        animate('300ms ease-out', style({ opacity: 1 }))
    ]),
    transition(':leave', [
        animate('200ms ease-in', style({ opacity: 0 }))
    ])
]);

export const slideInUp = trigger('slideInUp', [
    transition(':enter', [
        style({ transform: 'translateY(20px)', opacity: 0 }),
        animate('400ms cubic-bezier(0.35, 0, 0.25, 1)', style({ transform: 'translateY(0)', opacity: 1 }))
    ])
]);

export const staggerList = trigger('staggerList', [
    transition('* => *', [
        query(':enter', [
            style({ opacity: 0, transform: 'translateY(10px)' }),
            stagger(100, [
                animate('300ms ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
            ])
        ], { optional: true })
    ])
]);
