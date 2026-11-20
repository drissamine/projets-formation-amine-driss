import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Task } from '../../models/task.model';

@Component({
  selector: 'app-task-item',
  imports: [FormsModule],
  templateUrl: './task-item.html',
  styleUrl: './task-item.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TaskItem {
  @Input({ required: true }) task!: Task;
  @Output() remove = new EventEmitter<void>();
  @Output() toggle = new EventEmitter<void>();
  @Output() edit = new EventEmitter<{ id: number; title: string }>();

  // État d'édition
  isEditing = signal(false);
  editTitle = signal('');

  // Méthodes pour gérer les actions
  onRemove() {
    this.remove.emit();
  }

  onToggle() {
    if (!this.isEditing()) {
      this.toggle.emit();
    }
  }

  // Méthodes pour l'édition
  startEdit() {
    if (!this.task.completed) {
      this.isEditing.set(true);
      this.editTitle.set(this.task.title);
      // Focus automatique sur l'input après le rendu
      setTimeout(() => {
        const input = document.getElementById(`edit-${this.task.id}`) as HTMLInputElement;
        if (input) {
          input.focus();
          input.select();
        }
      }, 0);
    }
  }

  cancelEdit() {
    this.isEditing.set(false);
    this.editTitle.set('');
  }

  saveEdit() {
    const trimmedTitle = this.editTitle().trim();
    if (trimmedTitle && trimmedTitle !== this.task.title) {
      this.edit.emit({ id: this.task.id, title: trimmedTitle });
    }
    this.cancelEdit();
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.saveEdit();
    } else if (event.key === 'Escape') {
      this.cancelEdit();
    }
  }

  // Méthode trackBy pour optimiser le rendu
  trackByTaskId(index: number, task: Task): number {
    return task.id;
  }
}
