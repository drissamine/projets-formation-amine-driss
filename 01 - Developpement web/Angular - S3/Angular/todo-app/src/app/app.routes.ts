import { Routes } from '@angular/router';
import { TaskList } from './components/task-list/task-list';
import { About } from './pages/about/about';

export const routes: Routes = [
    { path: '', component: TaskList },
    { path: 'about', component: About },
];
