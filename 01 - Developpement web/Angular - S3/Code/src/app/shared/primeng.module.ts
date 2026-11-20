import { NgModule } from '@angular/core';
import { SelectModule } from 'primeng/select';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ChartModule } from 'primeng/chart';
import { ProgressBarModule } from 'primeng/progressbar';
import { MenuModule } from 'primeng/menu';
import { MenubarModule } from 'primeng/menubar';

@NgModule({
  imports: [
    SelectModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    TableModule,
    TagModule,
    ConfirmDialogModule,
    ToastModule,
    ChartModule,
    ProgressBarModule,
    MenuModule,
    MenubarModule
  ],
  exports: [
    SelectModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    TableModule,
    TagModule,
    ConfirmDialogModule,
    ToastModule,
    ChartModule,
    ProgressBarModule,
    MenuModule,
    MenubarModule
  ]
})
export class PrimeNgModule { }
