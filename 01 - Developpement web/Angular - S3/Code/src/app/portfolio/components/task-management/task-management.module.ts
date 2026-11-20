import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { TaskListComponent } from './task-list/task-list.component';
import { TaskDetailsComponent } from './task-details/task-details.component';
import { TaskCreationComponent } from './task-creation/task-creation.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// PrimeNG Modules
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@NgModule({
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    ButtonModule,
    TableModule,
    TagModule,
    InputTextModule,
    SelectModule,
    ToastModule,
    TaskListComponent,
    TaskDetailsComponent,
    TaskCreationComponent
  ],
  exports: [
    TaskListComponent,
    TaskDetailsComponent,
    TaskCreationComponent
  ],
  providers: [MessageService]
})
export class TaskManagementModule { }
