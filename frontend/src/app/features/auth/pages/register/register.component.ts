import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gray-50 px-4">
      <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <div class="text-center mb-8">
          <span class="material-icons text-5xl text-primary">person_add</span>
          <h1 class="text-2xl font-bold text-gray-900 mt-2">Crear Cuenta</h1>
          <p class="text-gray-500 mt-1">Registrate con tu correo institucional</p>
        </div>

        @if (error()) {
          <div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
            {{ error() }}
          </div>
        }

        <form (ngSubmit)="onSubmit()" class="space-y-5">
          <div>
            <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1">
              Nombre completo
            </label>
            <input id="fullName" type="text" [(ngModel)]="fullName" name="fullName" required
                   placeholder="Tu nombre completo"
                   class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors">
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Correo electronico
            </label>
            <input id="email" type="email" [(ngModel)]="email" name="email" required
                   placeholder="usuario@upao.edu.pe"
                   class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors">
            <p class="mt-1 text-xs text-gray-500">Solo se permiten correos &#64;upao.edu.pe</p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Contrasena
            </label>
            <input id="password" type="password" [(ngModel)]="password" name="password" required
                   placeholder="Minimo 6 caracteres"
                   class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors">
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
              Confirmar contrasena
            </label>
            <input id="confirmPassword" type="password" [(ngModel)]="confirmPassword" name="confirmPassword" required
                   placeholder="Repite tu contrasena"
                   class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors">
          </div>

          <button type="submit" [disabled]="loading()"
                  class="w-full py-2.5 bg-primary hover:bg-primary-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50">
            @if (loading()) {
              <span class="inline-flex items-center">
                <span class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                Registrando...
              </span>
            } @else {
              Crear Cuenta
            }
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-gray-500">
          Ya tienes cuenta?
          <a routerLink="/login" class="text-primary hover:text-primary-600 font-medium">
            Inicia sesion
          </a>
        </p>
      </div>
    </div>
  `,
})
export class RegisterComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  fullName = '';
  email = '';
  password = '';
  confirmPassword = '';
  loading = signal(false);
  error = signal('');

  onSubmit(): void {
    if (!this.fullName || !this.email || !this.password || !this.confirmPassword) {
      this.error.set('Complete todos los campos.');
      return;
    }

    if (!this.email.endsWith('@upao.edu.pe')) {
      this.error.set('Solo se permiten correos @upao.edu.pe');
      return;
    }

    if (this.password.length < 6) {
      this.error.set('La contrasena debe tener al menos 6 caracteres.');
      return;
    }

    if (this.password !== this.confirmPassword) {
      this.error.set('Las contrasenas no coinciden.');
      return;
    }

    this.loading.set(true);
    this.error.set('');

    this.auth.register({
      email: this.email,
      password: this.password,
      full_name: this.fullName
    }).subscribe({
      next: (response) => {
        this.loading.set(false);
        if (response.success) {
          this.router.navigate(['/chat']);
        }
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err.error?.message || 'Error al registrarse. Intente nuevamente.');
      }
    });
  }
}
