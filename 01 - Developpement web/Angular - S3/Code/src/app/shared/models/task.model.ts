export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  createdAt: Date;
  updatedAt: Date;
  dueDate: Date;
  assignedTo: string;
}

export interface TaskList {
  id: string;
  name: string;
  tasks: Task[];
  createdAt: Date;
  updatedAt: Date;
}
