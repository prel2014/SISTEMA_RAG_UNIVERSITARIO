import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <nav class="bg-primary text-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center space-x-3">
            <a routerLink="/" class="flex items-center space-x-2">
              <span class="material-icons text-2xl">school</span>
              <span class="text-xl font-bold">UPAO RAG</span>
            </a>
          </div>

          <!-- Nav links -->
          @if (auth.isAuthenticated()) {
            <div class="flex items-center space-x-4">
              <a routerLink="/chat" routerLinkActive="bg-primary-700"
                 class="px-3 py-2 rounded-md text-sm font-medium hover:bg-primary-600 transition-colors">
                <span class="material-icons text-sm align-middle mr-1">chat</span>
                Chat
              </a>

              @if (auth.isAdmin()) {
                <a routerLink="/admin" routerLinkActive="bg-primary-700"
                   class="px-3 py-2 rounded-md text-sm font-medium hover:bg-primary-600 transition-colors">
                  <span class="material-icons text-sm align-middle mr-1">admin_panel_settings</span>
                  Panel Admin
                </a>
              }

              <!-- User menu -->
              <div class="flex items-center space-x-3 ml-4 pl-4 border-l border-primary-400">
                <a routerLink="/profile" class="text-sm hover:text-primary-200 transition-colors">
                  {{ auth.user()?.full_name }}
                </a>
                <button (click)="auth.logout()"
                        class="px-3 py-1.5 text-sm bg-secondary hover:bg-secondary-600 rounded transition-colors">
                  Salir
                </button>
              </div>
            </div>
          } @else {
            <div class="flex items-center space-x-3">
              <a routerLink="/login"
                 class="px-4 py-2 text-sm font-medium hover:bg-primary-600 rounded transition-colors">
                Iniciar Sesion
              </a>
              <a routerLink="/register"
                 class="px-4 py-2 text-sm font-medium bg-secondary hover:bg-secondary-600 rounded transition-colors">
                Registrarse
              </a>
            </div>
          }
        </div>
      </div>
    </nav>
  `,
})
export class NavbarComponent {
  auth = inject(AuthService);
}
