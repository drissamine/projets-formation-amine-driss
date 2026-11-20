import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { fadeAnimation } from '../../animations/fade.animation';
// PrimeNG imports
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';

interface Message {
  severity: 'success' | 'info' | 'warn' | 'error';
  summary: string;
  detail: string;
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    InputTextModule,
    PasswordModule,
    ButtonModule,
    MessageModule
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
  animations: [fadeAnimation]
})
export class Login {
  loginForm: FormGroup;
  returnUrl: string;
  error = '';
  loading = false;
  messages: Message[] = [];

  constructor(
    private formBuilder: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    if (this.authService.isAuthenticated) {
      this.router.navigate(['/portfolio']);
    }
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/portfolio';
  }

  get f() { return this.loginForm.controls; }

  onSubmit() {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    // Effacer les messages précédents
    this.messages = [];

    // La connexion simulée est synchrone pour l'instant
    this.authService.login({
      email: this.f['email'].value,
      password: this.f['password'].value
    }).subscribe({
      next: (success) => {
        if (success) {
          this.router.navigate([this.returnUrl]);
        } else {
          this.error = 'Échec de la connexion';
          this.messages = [{
            severity: 'error' as const,
            summary: 'Erreur de connexion',
            detail: 'Email ou mot de passe incorrect'
          }];
          this.loading = false;
        }
      },
      error: () => {
        this.error = 'Une erreur est survenue';
        this.loading = false;
      }
    });
  }
}
