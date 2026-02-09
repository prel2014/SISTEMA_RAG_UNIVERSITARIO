import { Component, EventEmitter, Input, Output, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService } from '../../services/document.service';
import { CategoryService } from '../../services/category.service';
import { Category } from '../../../../core/models/document.model';
import { ToastService } from '../../../../shared/components/toast/toast.component';

@Component({
  selector: 'app-document-upload-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    @if (isOpen) {
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full mx-4 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Subir Documento</h3>

          <!-- Drag & drop area -->
          <div (drop)="onDrop($event)" (dragover)="onDragOver($event)" (dragleave)="isDragging.set(false)"
               class="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer"
               [ngClass]="isDragging() ? 'border-primary bg-primary-50' : 'border-gray-300 hover:border-primary'"
               (click)="fileInput.click()">
            <input #fileInput type="file" (change)="onFileSelected($event)" class="hidden"
                   accept=".pdf,.docx,.xlsx,.xls,.txt,.png,.jpg,.jpeg">
            <span class="material-icons text-4xl text-gray-400 mb-2">cloud_upload</span>
            @if (selectedFile()) {
              <p class="text-sm font-medium text-primary">{{ selectedFile()!.name }}</p>
              <p class="text-xs text-gray-500">{{ (selectedFile()!.size / 1024 / 1024).toFixed(2) }} MB</p>
            } @else {
              <p class="text-sm text-gray-600">Arrastra un archivo aqui o haz clic para seleccionar</p>
              <p class="text-xs text-gray-400 mt-1">PDF, DOCX, XLSX, TXT, PNG, JPG (max 50MB)</p>
            }
          </div>

          <!-- Title -->
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Titulo</label>
            <input type="text" [(ngModel)]="title"
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm">
          </div>

          <!-- Category -->
          <div class="mt-3">
            <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
            <select [(ngModel)]="categoryId"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm">
              <option value="">Sin categoria</option>
              @for (cat of categories; track cat.id) {
                <option [value]="cat.id">{{ cat.name }}</option>
              }
            </select>
          </div>

          <!-- Actions -->
          <div class="mt-6 flex justify-end space-x-3">
            <button (click)="close.emit()" class="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg">
              Cancelar
            </button>
            <button (click)="onUpload()" [disabled]="uploading() || !selectedFile()"
                    class="px-4 py-2 text-sm text-white bg-primary hover:bg-primary-600 rounded-lg disabled:opacity-50">
              @if (uploading()) {
                Subiendo...
              } @else {
                Subir Documento
              }
            </button>
          </div>
        </div>
      </div>
    }
  `,
})
export class DocumentUploadDialogComponent {
  @Input() isOpen = false;
  @Input() categories: Category[] = [];
  @Output() close = new EventEmitter<void>();
  @Output() uploaded = new EventEmitter<void>();

  private docService = inject(DocumentService);
  private toast = inject(ToastService);

  selectedFile = signal<File | null>(null);
  isDragging = signal(false);
  uploading = signal(false);
  title = '';
  categoryId = '';

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFile.set(input.files[0]);
      if (!this.title) this.title = input.files[0].name;
    }
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(false);
    if (event.dataTransfer?.files.length) {
      this.selectedFile.set(event.dataTransfer.files[0]);
      if (!this.title) this.title = event.dataTransfer.files[0].name;
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(true);
  }

  onUpload(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.uploading.set(true);
    this.docService.upload(file, this.title || file.name, this.categoryId || undefined).subscribe({
      next: () => {
        this.uploading.set(false);
        this.toast.success('Documento subido exitosamente.');
        this.reset();
        this.uploaded.emit();
        this.close.emit();
      },
      error: (err) => {
        this.uploading.set(false);
        this.toast.error(err.error?.message || 'Error al subir documento.');
      }
    });
  }

  private reset(): void {
    this.selectedFile.set(null);
    this.title = '';
    this.categoryId = '';
  }
}
