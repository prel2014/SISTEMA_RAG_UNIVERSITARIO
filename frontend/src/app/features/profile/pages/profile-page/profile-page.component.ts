import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="max-w-2xl mx-auto py-12 px-4">
      <h1 class="text-2xl font-bold text-gray-800 mb-6">Mi Perfil</h1>

      @if (auth.user(); as user) {
        <div class="bg-white rounded-xl shadow-sm border p-6">
          <div class="flex items-center space-x-4 mb-6">
            <div class="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {{ user.full_name.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">{{ user.full_name }}</h2>
              <p class="text-gray-500">{{ user.email }}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-500">Rol</p>
              <p class="font-medium text-gray-800">{{ user.role === 'admin' ? 'Administrador' : 'Usuario' }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-500">Estado</p>
              <p class="font-medium" [class]="user.is_active ? 'text-green-600' : 'text-red-600'">
                {{ user.is_active ? 'Activo' : 'Inactivo' }}
              </p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4 col-span-2">
              <p class="text-sm text-gray-500">Miembro desde</p>
              <p class="font-medium text-gray-800">{{ formatDate(user.created_at) }}</p>
            </div>
          </div>
        </div>
      }
    </div>
  `,
})
export class ProfilePageComponent {
  auth = inject(AuthService);

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('es-PE', {
      day: '2-digit', month: 'long', year: 'numeric'
    });
  }
}
