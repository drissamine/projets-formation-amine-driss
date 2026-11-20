import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MessageService } from 'primeng/api';

// PrimeNG Modules
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';
import { ToastModule } from 'primeng/toast';

@Component({
  selector: 'app-task-creation',
  standalone: true,
  templateUrl: './task-creation.component.html',
  styleUrl: './task-creation.component.scss',
  imports: [
    CommonModule,
    ReactiveFormsModule,
    CardModule,
    ButtonModule,
    SelectModule,
    ToastModule
  ],
  providers: [MessageService]
})
export class TaskCreationComponent {
  taskForm: FormGroup;

  priorityOptions = [
    { label: 'Faible', value: 'low' },
    { label: 'Moyenne', value: 'medium' },
    { label: 'Élevée', value: 'high' }
  ];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private messageService: MessageService
  ) {
    this.taskForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required]],
      priority: ['medium', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.taskForm.valid) {
      // Here you would save the task
      this.messageService.add({
        severity: 'success',
        summary: 'Succès',
        detail: 'Tâche créée avec succès'
      });

      // Navigate back to task list
      setTimeout(() => {
        this.router.navigate(['/portfolio/tasks']);
      }, 1500);
    } else {
      this.messageService.add({
        severity: 'error',
        summary: 'Erreur',
        detail: 'Veuillez corriger les erreurs du formulaire'
      });
    }
  }

  onCancel(): void {
    this.router.navigate(['/portfolio/tasks']);
  }

  get title() { return this.taskForm.get('title'); }
  get description() { return this.taskForm.get('description'); }
}
