import { Component, inject, ChangeDetectionStrategy, signal, computed, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { trigger, transition, style, animate } from '@angular/animations';
import { Task } from '../../models/task.model';
import { TaskItem } from '../task-item/task-item';
import { TaskService } from '../../services/task';

@Component({
  selector: 'app-task-list',
  imports: [TaskItem, FormsModule],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
  animations: [
    trigger('fade', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(-10px)' }),
        animate('200ms ease-out', style({ opacity: 1, transform: 'translateY(0)' }))
      ]),
      transition(':leave', [
        animate('200ms ease-in', style({ opacity: 0, transform: 'translateX(10px)' }))
      ])
    ])
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TaskList implements OnInit, OnDestroy {
  private taskService = inject(TaskService);
  private keydownHandler?: (event: KeyboardEvent) => void;

  // États réactifs pour le filtrage
  filterStatus = signal<'all' | 'active' | 'completed'>('all');
  errorMessage = signal<string>('');

  // Computed values pour les tâches filtrées et les statistiques
  filteredTasks = computed(() =>
    this.taskService.getTasksByStatus(this.filterStatus())
  );

  remainingTasks = this.taskService.remainingTasks;
  allCompleted = this.taskService.allCompleted;

  // Getter pour accéder aux tâches directement
  get tasks() {
    return this.taskService.tasks;
  }

  // Propriétés du composant
  newTaskTitle = '';

  ngOnInit() {
    // Ajouter les raccourcis clavier
    this.keydownHandler = (event: KeyboardEvent) => {
      // Ctrl/Cmd + N : Nouvelle tâche (focus sur l'input)
      if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        const input = document.querySelector('input[placeholder="Nouvelle tâche..."]') as HTMLInputElement;
        if (input) {
          input.focus();
        }
      }

      // Ctrl/Cmd + A : Toggle all tasks
      if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
        event.preventDefault();
        if (this.tasks().length > 0) {
          this.toggleAllTasks();
        }
      }

      // Ctrl/Cmd + Delete : Clear completed
      if ((event.ctrlKey || event.metaKey) && event.key === 'Delete') {
        event.preventDefault();
        if (this.tasks().length - this.remainingTasks() > 0) {
          this.clearCompletedTasks();
        }
      }

      // 1, 2, 3 : Quick filter
      if (!event.ctrlKey && !event.metaKey && !event.altKey) {
        switch (event.key) {
          case '1':
            this.setFilter('all');
            break;
          case '2':
            this.setFilter('active');
            break;
          case '3':
            this.setFilter('completed');
            break;
        }
      }
    };

    document.addEventListener('keydown', this.keydownHandler);
  }

  ngOnDestroy() {
    if (this.keydownHandler) {
      document.removeEventListener('keydown', this.keydownHandler);
    }
  }

  // Méthodes d'action
  addTask() {
    this.clearError();

    if (!this.newTaskTitle.trim()) {
      this.setError('Veuillez saisir un titre pour la tâche');
      return;
    }

    if (this.newTaskTitle.length > 100) {
      this.setError('Le titre ne peut pas dépasser 100 caractères');
      return;
    }

    try {
      this.taskService.addTask(this.newTaskTitle);
      this.newTaskTitle = '';
    } catch (error) {
      this.setError(error instanceof Error ? error.message : 'Erreur lors de l\'ajout de la tâche');
    }
  }

  deleteTask(task: Task) {
    this.taskService.removeTask(task.id);
    this.clearError();
  }

  toggleTask(task: Task) {
    this.taskService.toggleTask(task.id);
    this.clearError();
  }

  editTask(event: { id: number; title: string }) {
    try {
      this.taskService.editTask(event.id, event.title);
      this.clearError();
    } catch (error) {
      this.setError(error instanceof Error ? error.message : 'Erreur lors de la modification de la tâche');
    }
  }

  // Nouvelles méthodes pour les améliorations
  clearCompletedTasks() {
    this.taskService.clearCompleted();
    this.clearError();
  }

  toggleAllTasks() {
    this.taskService.toggleAll();
    this.clearError();
  }

  setFilter(status: 'all' | 'active' | 'completed') {
    this.filterStatus.set(status);
    this.clearError();
  }

  // Gestion des erreurs
  private setError(message: string) {
    this.errorMessage.set(message);
    // Auto-clear error after 5 seconds
    setTimeout(() => this.clearError(), 5000);
  }

  private clearError() {
    this.errorMessage.set('');
  }




}
