import { Injectable, signal, effect, computed } from '@angular/core';
import { Task } from '../models/task.model';

@Injectable({
  providedIn: 'root',
})
export class TaskService {
  tasks = signal<Task[]>([]);

  constructor() {
    // Charger les tâches depuis le localStorage au démarrage
    const savedTasks = localStorage.getItem('tasks');
    if (savedTasks) {
      try {
        const parsed = JSON.parse(savedTasks);
        if (Array.isArray(parsed)) {
          this.tasks.set(parsed);
        }
      } catch (error) {
        console.warn('Failed to parse saved tasks from localStorage:', error);
      }
    }

    // Sauvegarder les tâches à chaque changement
    effect(() => {
      localStorage.setItem('tasks', JSON.stringify(this.tasks()));
    });
  }

  // État dérivé : nombre de tâches restantes
  remainingTasks = computed(() => this.tasks().filter(t => !t.completed).length);

  // État dérivé : toutes les tâches complétées
  allCompleted = computed(() => this.tasks().length > 0 && this.tasks().every(t => t.completed));

  addTask(title: string) {
    const trimmedTitle = title.trim();
    
    // Validation
    if (!trimmedTitle) {
      throw new Error('Le titre de la tâche ne peut pas être vide');
    }
    
    if (trimmedTitle.length > 100) {
      throw new Error('Le titre de la tâche ne peut pas dépasser 100 caractères');
    }

    const newTask: Task = {
      id: Date.now(),
      title: trimmedTitle,
      completed: false
    };
    
    this.tasks.update(tasks => [...tasks, newTask]);
  }

  removeTask(id: number) {
    this.tasks.update(tasks => tasks.filter(t => t.id !== id));
  }

  toggleTask(id: number) {
    this.tasks.update(tasks =>
      tasks.map(t => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  }

  editTask(id: number, newTitle: string) {
    const trimmedTitle = newTitle.trim();
    
    // Validation
    if (!trimmedTitle) {
      throw new Error('Le titre de la tâche ne peut pas être vide');
    }
    
    if (trimmedTitle.length > 100) {
      throw new Error('Le titre de la tâche ne peut pas dépasser 100 caractères');
    }

    this.tasks.update(tasks =>
      tasks.map(t => (t.id === id ? { ...t, title: trimmedTitle } : t))
    );
  }

  // Nouvelles méthodes pour les améliorations
  clearCompleted() {
    this.tasks.update(tasks => tasks.filter(t => !t.completed));
  }

  toggleAll() {
    const allCompleted = this.allCompleted();
    this.tasks.update(tasks =>
      tasks.map(t => ({ ...t, completed: !allCompleted }))
    );
  }

  getTasksByStatus(status: 'all' | 'active' | 'completed') {
    switch (status) {
      case 'active':
        return this.tasks().filter(t => !t.completed);
      case 'completed':
        return this.tasks().filter(t => t.completed);
      default:
        return this.tasks();
    }
  }
}
