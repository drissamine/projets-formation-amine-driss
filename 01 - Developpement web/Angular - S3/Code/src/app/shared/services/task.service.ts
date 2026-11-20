import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { Task, TaskList } from '../models/task.model';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private tasks: Task[] = [
    {
      id: '1',
      title: 'Analyser les performances du portefeuille',
      description: 'Analyser les performances des actions pour le mois en cours',
      status: 'todo',
      priority: 'high',
      createdAt: new Date(),
      updatedAt: new Date(),
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      assignedTo: 'Utilisateur 1'
    },
    {
      id: '2',
      title: 'Mettre à jour les données du marché',
      description: 'Mettre à jour les données du marché pour les actions suivies',
      status: 'in-progress',
      priority: 'medium',
      createdAt: new Date(),
      updatedAt: new Date(),
      dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
      assignedTo: 'Utilisateur 2'
    },
    {
      id: '3',
      title: 'Créer un rapport de performance',
      description: 'Créer un rapport de performance pour le trimestre',
      status: 'done',
      priority: 'low',
      createdAt: new Date(),
      updatedAt: new Date(),
      dueDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      assignedTo: 'Utilisateur 3'
    }
  ];

  private tasksSubject = new BehaviorSubject<Task[]>(this.tasks);

  constructor() { }

  getTasks(): Observable<Task[]> {
    return this.tasksSubject.asObservable();
  }

  getTaskById(id: string): Observable<Task | undefined> {
    const task = this.tasks.find(t => t.id === id);
    return of(task);
  }

  addTask(task: Task): Observable<Task> {
    this.tasks.push(task);
    this.tasksSubject.next(this.tasks);
    return of(task);
  }

  updateTask(id: string, updates: Partial<Task>): Observable<Task | undefined> {
    const index = this.tasks.findIndex(t => t.id === id);
    if (index !== -1) {
      this.tasks[index] = { ...this.tasks[index], ...updates, updatedAt: new Date() };
      this.tasksSubject.next(this.tasks);
      return of(this.tasks[index]);
    }
    return of(undefined);
  }

  deleteTask(id: string): Observable<boolean> {
    const index = this.tasks.findIndex(t => t.id === id);
    if (index !== -1) {
      this.tasks.splice(index, 1);
      this.tasksSubject.next(this.tasks);
      return of(true);
    }
    return of(false);
  }

  getTasksByStatus(status: string): Observable<Task[]> {
    const filteredTasks = this.tasks.filter(t => t.status === status);
    return of(filteredTasks);
  }

  getTasksByPriority(priority: string): Observable<Task[]> {
    const filteredTasks = this.tasks.filter(t => t.priority === priority);
    return of(filteredTasks);
  }
}