import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AsyncPipe, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

// PrimeNG Modules
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  createdAt: Date;
  updatedAt: Date;
}

@Component({
  selector: 'app-task-list',
  standalone: true,
  templateUrl: './task-list.component.html',
  styleUrl: './task-list.component.scss',
  imports: [
    AsyncPipe,
    DatePipe,
    FormsModule,
    CardModule,
    ButtonModule,
    TableModule,
    TagModule
  ]
})
export class TaskListComponent {
  tasks$: Observable<Task[]>;

  constructor(
    private router: Router
  ) {
    // Mock tasks for now
    this.tasks$ = new Observable(observer => {
      observer.next([
        {
          id: '1',
          title: 'Acheter des actions Apple',
          description: 'Rechercher et acheter 10 actions AAPL',
          status: 'pending',
          priority: 'high',
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: '2',
          title: 'Vendre positions Google',
          description: 'Évaluer et vendre les actions GOOGL si profit > 5%',
          status: 'in_progress',
          priority: 'medium',
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ]);
    });
  }

  getStatusLabel(status: string): string {
    const labels = {
      'pending': 'En attente',
      'in_progress': 'En cours',
      'completed': 'Terminée'
    };
    return labels[status as keyof typeof labels] || status;
  }

  getStatusSeverity(status: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast' {
    const severities: Record<string, 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast'> = {
      'pending': 'warn',
      'in_progress': 'info',
      'completed': 'success'
    };
    return severities[status] || 'info';
  }

  getPriorityLabel(priority: string): string {
    const labels = {
      'low': 'Faible',
      'medium': 'Moyenne',
      'high': 'Élevée'
    };
    return labels[priority as keyof typeof labels] || priority;
  }

  getPrioritySeverity(priority: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast' {
    const severities: Record<string, 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast'> = {
      'low': 'success',
      'medium': 'warn',
      'high': 'danger'
    };
    return severities[priority] || 'info';
  }

  createTask(): void {
    this.router.navigate(['/portfolio/tasks/create']);
  }

  viewTask(taskId: string): void {
    this.router.navigate(['/portfolio/tasks', taskId]);
  }

  editTask(taskId: string): void {
    this.router.navigate(['/portfolio/tasks', taskId, 'edit']);
  }

  deleteTask(taskId: string): void {
    // Implement delete logic
    // TODO: Add confirmation dialog and actual delete functionality
  }
}
