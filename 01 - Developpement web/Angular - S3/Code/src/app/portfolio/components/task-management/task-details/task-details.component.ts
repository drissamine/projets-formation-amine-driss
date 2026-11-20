import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';

// PrimeNG Modules
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
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
  selector: 'app-task-details',
  standalone: true,
  templateUrl: './task-details.component.html',
  styleUrl: './task-details.component.scss',
  imports: [
    CommonModule,
    DatePipe,
    CardModule,
    ButtonModule,
    TagModule
  ]
})
export class TaskDetailsComponent implements OnInit {
  task: Task | null = null;
  taskId: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.taskId = this.route.snapshot.params['id'];
    this.loadTask();
  }

  private loadTask(): void {
    // Mock task data - replace with actual service call
    this.task = {
      id: this.taskId,
      title: 'Acheter des actions Apple',
      description: 'Rechercher et acheter 10 actions AAPL en analysant les indicateurs techniques et fondamentaux.',
      status: 'in_progress',
      priority: 'high',
      createdAt: new Date('2025-12-27'),
      updatedAt: new Date('2025-12-28')
    };
  }

  get taskSafe(): Task {
    return this.task!;
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

  goBack(): void {
    this.router.navigate(['/portfolio/tasks']);
  }

  editTask(): void {
    this.router.navigate(['/portfolio/tasks', this.taskId, 'edit']);
  }
}
