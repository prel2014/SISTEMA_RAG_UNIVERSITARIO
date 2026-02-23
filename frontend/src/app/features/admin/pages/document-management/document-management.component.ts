import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService } from '../../services/document.service';
import { CategoryService } from '../../services/category.service';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { DocumentUploadDialogComponent } from '../../components/document-upload-dialog/document-upload-dialog.component';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';
import { ConfirmDialogComponent } from '../../../../shared/components/confirm-dialog/confirm-dialog.component';
import { ToastService } from '../../../../shared/components/toast/toast.component';
import { Document, Category } from '../../../../core/models/document.model';
import { PAGE_SIZE } from '../../../../shared/constants/pagination';
import { getStatusLabel, getStatusBadgeClass } from '../../../../shared/utils/status.utils';

@Component({
  selector: 'app-document-management',
  standalone: true,
  imports: [CommonModule, FormsModule, AdminSidebarComponent, DocumentUploadDialogComponent, PaginationComponent, ConfirmDialogComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1 p-6 bg-gray-50">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-bold text-gray-800">Gestion de Documentos</h1>
          <button (click)="showUpload.set(true)"
                  class="px-4 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors">
            <span class="material-icons text-sm align-middle mr-1">upload</span>
            Subir Documento
          </button>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-xl shadow-sm border p-4 mb-4 flex gap-4">
          <input type="text" [(ngModel)]="searchQuery" (input)="loadDocuments()"
                 placeholder="Buscar documentos..."
                 class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none">
          <select [(ngModel)]="filterCategory" (change)="loadDocuments()"
                  class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
            <option value="">Todas las categorias</option>
            @for (cat of categories(); track cat.id) {
              <option [value]="cat.id">{{ cat.name }}</option>
            }
          </select>
          <select [(ngModel)]="filterStatus" (change)="loadDocuments()"
                  class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
            <option value="">Todos los estados</option>
            <option value="completed">Completado</option>
            <option value="processing">Procesando</option>
            <option value="pending">Pendiente</option>
            <option value="failed">Fallido</option>
          </select>
        </div>

        <!-- Table -->
        <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50 border-b">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Titulo</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoria</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunks</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              @for (doc of documents(); track doc.id) {
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-3">
                    <div class="text-sm font-medium text-gray-900">{{ doc.title }}</div>
                    <div class="text-xs text-gray-500">{{ doc.original_filename }}</div>
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-xs font-medium px-2 py-1 bg-gray-100 rounded uppercase">{{ doc.file_type }}</span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ doc.category?.name || '-' }}</td>
                  <td class="px-4 py-3">
                    <span class="text-xs font-medium px-2 py-1 rounded-full"
                          [ngClass]="getStatusBadgeClass(doc.processing_status)">
                      {{ getStatusLabel(doc.processing_status) }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ doc.chunk_count }}</td>
                  <td class="px-4 py-3">
                    <div class="flex space-x-1">
                      <button (click)="reprocessDoc(doc.id)" title="Reprocesar"
                              class="p-1 text-gray-400 hover:text-primary rounded">
                        <span class="material-icons text-sm">refresh</span>
                      </button>
                      <button (click)="confirmDelete(doc.id)" title="Eliminar"
                              class="p-1 text-gray-400 hover:text-red-600 rounded">
                        <span class="material-icons text-sm">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              } @empty {
                <tr>
                  <td colspan="6" class="px-4 py-8 text-center text-gray-400">No hay documentos.</td>
                </tr>
              }
            </tbody>
          </table>
          <app-pagination [total]="totalDocs()" [currentPage]="currentPage" [perPage]="PAGE_SIZE" (pageChange)="onPageChange($event)" />
        </div>

        <!-- Upload dialog -->
        <app-document-upload-dialog [isOpen]="showUpload()" [categories]="categories()"
                                    (close)="showUpload.set(false)" (uploaded)="loadDocuments()" />

        <!-- Confirm delete -->
        <app-confirm-dialog [isOpen]="!!deleteId()" title="Eliminar Documento"
                            message="Esta seguro de eliminar este documento? Esta accion no se puede deshacer."
                            confirmText="Eliminar"
                            (confirmed)="deleteDoc()" (cancelled)="deleteId.set('')" />
      </div>
    </div>
  `,
})
export class DocumentManagementComponent implements OnInit {
  private docService = inject(DocumentService);
  private catService = inject(CategoryService);
  private toast = inject(ToastService);

  readonly PAGE_SIZE = PAGE_SIZE;
  readonly getStatusLabel = getStatusLabel;
  readonly getStatusBadgeClass = getStatusBadgeClass;

  documents = signal<Document[]>([]);
  categories = signal<Category[]>([]);
  totalDocs = signal(0);
  showUpload = signal(false);
  deleteId = signal('');

  searchQuery = '';
  filterCategory = '';
  filterStatus = '';
  currentPage = 1;

  ngOnInit(): void {
    this.loadDocuments();
    this.catService.listAll().subscribe({
      next: (res) => this.categories.set(res.data.categories),
    });
  }

  loadDocuments(): void {
    this.docService.list({
      page: this.currentPage,
      search: this.searchQuery,
      category_id: this.filterCategory,
      status: this.filterStatus,
    }).subscribe({
      next: (res) => {
        this.documents.set(res.data);
        this.totalDocs.set(res.pagination.total);
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadDocuments();
  }

  confirmDelete(id: string): void {
    this.deleteId.set(id);
  }

  deleteDoc(): void {
    const id = this.deleteId();
    if (!id) return;
    this.docService.delete(id).subscribe({
      next: () => {
        this.toast.success('Documento eliminado.');
        this.deleteId.set('');
        this.loadDocuments();
      },
      error: () => this.toast.error('Error al eliminar documento.'),
    });
  }

  reprocessDoc(id: string): void {
    this.docService.reprocess(id).subscribe({
      next: () => {
        this.toast.success('Reprocesamiento iniciado.');
        this.loadDocuments();
      },
      error: () => this.toast.error('Error al reprocesar.'),
    });
  }
}
