import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-admin-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <div class="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
      <div class="p-4">
        <h2 class="text-lg font-semibold text-gray-800">Panel de Administracion</h2>
      </div>
      <nav class="space-y-1 px-2">
        @for (item of menuItems; track item.path) {
          <a [routerLink]="['/admin', item.path]" routerLinkActive="bg-primary-50 text-primary border-l-2 border-primary"
             class="flex items-center px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 rounded-r-lg transition-colors">
            <span class="material-icons text-lg mr-3">{{ item.icon }}</span>
            {{ item.label }}
          </a>
        }
      </nav>
    </div>
  `,
})
export class AdminSidebarComponent {
  menuItems = [
    { path: 'dashboard', icon: 'dashboard', label: 'Dashboard' },
    { path: 'documents', icon: 'description', label: 'Documentos' },
    { path: 'categories', icon: 'category', label: 'Categorias' },
    { path: 'users', icon: 'people', label: 'Usuarios' },
    { path: 'rag-config', icon: 'tune', label: 'Configuracion RAG' },
    { path: 'test-chat', icon: 'chat', label: 'Probar Chat' },
  ];
}
