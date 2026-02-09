import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CategoryService } from '../../services/category.service';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { ConfirmDialogComponent } from '../../../../shared/components/confirm-dialog/confirm-dialog.component';
import { ToastService } from '../../../../shared/components/toast/toast.component';
import { Category } from '../../../../core/models/document.model';

@Component({
  selector: 'app-category-management',
  standalone: true,
  imports: [CommonModule, FormsModule, AdminSidebarComponent, ConfirmDialogComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1 p-6 bg-gray-50">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-bold text-gray-800">Gestion de Categorias</h1>
          <button (click)="showForm.set(true); editing.set(null)"
                  class="px-4 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg text-sm font-medium">
            <span class="material-icons text-sm align-middle mr-1">add</span>
            Nueva Categoria
          </button>
        </div>

        <!-- Form (create/edit) -->
        @if (showForm()) {
          <div class="bg-white rounded-xl shadow-sm border p-6 mb-6">
            <h3 class="font-semibold text-gray-800 mb-4">{{ editing() ? 'Editar' : 'Nueva' }} Categoria</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                <input type="text" [(ngModel)]="formName"
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
                <input type="color" [(ngModel)]="formColor" class="h-10 w-20 rounded cursor-pointer">
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Descripcion</label>
                <input type="text" [(ngModel)]="formDescription"
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
              </div>
            </div>
            <div class="mt-4 flex space-x-3">
              <button (click)="saveCategory()" class="px-4 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg text-sm">
                {{ editing() ? 'Actualizar' : 'Crear' }}
              </button>
              <button (click)="showForm.set(false)" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm">Cancelar</button>
            </div>
          </div>
        }

        <!-- Table -->
        <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50 border-b">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Color</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripcion</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Documentos</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              @for (cat of categories(); track cat.id) {
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-3">
                    <div class="w-6 h-6 rounded-full" [style.background-color]="cat.color"></div>
                  </td>
                  <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ cat.name }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ cat.description || '-' }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ cat.document_count }}</td>
                  <td class="px-4 py-3">
                    <span class="text-xs px-2 py-1 rounded-full"
                          [ngClass]="cat.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
                      {{ cat.is_active ? 'Activa' : 'Inactiva' }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex space-x-1">
                      <button (click)="editCategory(cat)" class="p-1 text-gray-400 hover:text-primary rounded">
                        <span class="material-icons text-sm">edit</span>
                      </button>
                      <button (click)="confirmDelete(cat.id)" class="p-1 text-gray-400 hover:text-red-600 rounded">
                        <span class="material-icons text-sm">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>

        <app-confirm-dialog [isOpen]="!!deleteId()" title="Eliminar Categoria"
                            message="Esta seguro de eliminar esta categoria?"
                            (confirmed)="deleteCategory()" (cancelled)="deleteId.set('')" />
      </div>
    </div>
  `,
})
export class CategoryManagementComponent implements OnInit {
  private catService = inject(CategoryService);
  private toast = inject(ToastService);

  categories = signal<Category[]>([]);
  showForm = signal(false);
  editing = signal<Category | null>(null);
  deleteId = signal('');

  formName = '';
  formDescription = '';
  formColor = '#1E3A5F';

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories(): void {
    this.catService.listAll().subscribe({
      next: (res) => this.categories.set(res.data.categories),
    });
  }

  editCategory(cat: Category): void {
    this.editing.set(cat);
    this.formName = cat.name;
    this.formDescription = cat.description || '';
    this.formColor = cat.color;
    this.showForm.set(true);
  }

  saveCategory(): void {
    const data = { name: this.formName, description: this.formDescription, color: this.formColor };
    const ed = this.editing();
    const obs = ed ? this.catService.update(ed.id, data) : this.catService.create(data);
    obs.subscribe({
      next: () => {
        this.toast.success(ed ? 'Categoria actualizada.' : 'Categoria creada.');
        this.showForm.set(false);
        this.formName = '';
        this.formDescription = '';
        this.loadCategories();
      },
      error: (err) => this.toast.error(err.error?.message || 'Error al guardar.'),
    });
  }

  confirmDelete(id: string): void {
    this.deleteId.set(id);
  }

  deleteCategory(): void {
    this.catService.delete(this.deleteId()).subscribe({
      next: () => {
        this.toast.success('Categoria eliminada.');
        this.deleteId.set('');
        this.loadCategories();
      },
      error: (err) => this.toast.error(err.error?.message || 'Error al eliminar.'),
    });
  }
}
