import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';
import { ToastService } from '../../../../shared/components/toast/toast.component';
import { User, PaginatedResponse, ApiResponse } from '../../../../core/models/user.model';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule, AdminSidebarComponent, PaginationComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1 p-6 bg-gray-50">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Gestion de Usuarios</h1>

        <!-- Search -->
        <div class="bg-white rounded-xl shadow-sm border p-4 mb-4">
          <input type="text" [(ngModel)]="searchQuery" (input)="loadUsers()"
                 placeholder="Buscar por nombre o email..."
                 class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
        </div>

        <!-- Table -->
        <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50 border-b">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Registro</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              @for (user of users(); track user.id) {
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ user.full_name }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ user.email }}</td>
                  <td class="px-4 py-3">
                    <span class="text-xs px-2 py-1 rounded-full"
                          [ngClass]="user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
                      {{ user.role === 'admin' ? 'Administrador' : 'Usuario' }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-xs px-2 py-1 rounded-full"
                          [ngClass]="user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                      {{ user.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(user.created_at) }}</td>
                  <td class="px-4 py-3">
                    @if (user.role !== 'admin') {
                      <button (click)="toggleActive(user)"
                              class="text-xs px-3 py-1 rounded border transition-colors"
                              [ngClass]="user.is_active ? 'border-red-300 text-red-600 hover:bg-red-50' : 'border-green-300 text-green-600 hover:bg-green-50'">
                        {{ user.is_active ? 'Desactivar' : 'Activar' }}
                      </button>
                    }
                  </td>
                </tr>
              }
            </tbody>
          </table>
          <app-pagination [total]="totalUsers()" [currentPage]="currentPage" [perPage]="20" (pageChange)="onPageChange($event)" />
        </div>
      </div>
    </div>
  `,
})
export class UserManagementComponent implements OnInit {
  private http = inject(HttpClient);
  private toast = inject(ToastService);

  users = signal<User[]>([]);
  totalUsers = signal(0);
  searchQuery = '';
  currentPage = 1;

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    let params = new HttpParams().set('page', this.currentPage.toString());
    if (this.searchQuery) params = params.set('search', this.searchQuery);

    this.http.get<PaginatedResponse<User>>(`${environment.apiUrl}/users`, { params }).subscribe({
      next: (res) => {
        this.users.set(res.data);
        this.totalUsers.set(res.pagination.total);
      }
    });
  }

  toggleActive(user: User): void {
    this.http.put<ApiResponse<{ user: User }>>(`${environment.apiUrl}/users/${user.id}/toggle-active`, {}).subscribe({
      next: (res) => {
        this.toast.success(res.message);
        this.loadUsers();
      },
      error: (err) => this.toast.error(err.error?.message || 'Error al cambiar estado.'),
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadUsers();
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' });
  }
}
