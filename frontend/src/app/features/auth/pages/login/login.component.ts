import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gray-50 px-4">
      <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <span class="material-icons text-5xl text-primary">school</span>
          <h1 class="text-2xl font-bold text-gray-900 mt-2">Bienvenido a UPAO RAG</h1>
          <p class="text-gray-500 mt-1">Ingresa tus credenciales para continuar</p>
        </div>

        <!-- Error -->
        @if (error()) {
          <div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
            {{ error() }}
          </div>
        }

        <!-- Form -->
        <form (ngSubmit)="onSubmit()" class="space-y-5">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Correo electronico
            </label>
            <input id="email" type="email" [(ngModel)]="email" name="email" required
                   placeholder="usuario@upao.edu.pe"
                   class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors">
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Contrasena
            </label>
            <input id="password" type="password" [(ngModel)]="password" name="password" required
                   placeholder="Tu contrasena"
                   class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors">
          </div>

          <button type="submit" [disabled]="loading()"
                  class="w-full py-2.5 bg-primary hover:bg-primary-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50">
            @if (loading()) {
              <span class="inline-flex items-center">
                <span class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                Ingresando...
              </span>
            } @else {
              Iniciar Sesion
            }
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-gray-500">
          No tienes cuenta?
          <a routerLink="/register" class="text-primary hover:text-primary-600 font-medium">
            Registrate aqui
          </a>
        </p>
      </div>
    </div>
  `,
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  loading = signal(false);
  error = signal('');

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error.set('Complete todos los campos.');
      return;
    }

    this.loading.set(true);
    this.error.set('');

    this.auth.login({ email: this.email, password: this.password }).subscribe({
      next: (response) => {
        this.loading.set(false);
        if (response.success) {
          const user = response.data.user;
          this.router.navigate([user.role === 'admin' ? '/admin' : '/chat']);
        }
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.error?.message || 'Error al iniciar sesion. Intente nuevamente.');
      }
    });
  }
}
