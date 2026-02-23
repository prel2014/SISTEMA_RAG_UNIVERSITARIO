import { Component, EventEmitter, Input, Output, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService } from '../../services/document.service';
import { Category, BatchUploadResult } from '../../../../core/models/document.model';
import { ToastService } from '../../../../shared/components/toast/toast.component';

@Component({
  selector: 'app-document-upload-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    @if (isOpen) {
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full mx-4 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Subir Documento(s)</h3>

          @if (uploadResults().length === 0) {
            <!-- Drag & drop area -->
            <div (drop)="onDrop($event)" (dragover)="onDragOver($event)" (dragleave)="isDragging.set(false)"
                 class="border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer"
                 [ngClass]="isDragging() ? 'border-primary bg-primary-50' : 'border-gray-300 hover:border-primary'"
                 (click)="fileInput.click()">
              <input #fileInput type="file" multiple (change)="onFileSelected($event)" class="hidden"
                     accept=".pdf,.docx,.xlsx,.xls">
              <span class="material-icons text-4xl text-gray-400 mb-2">cloud_upload</span>
              @if (selectedFiles().length === 0) {
                <p class="text-sm text-gray-600">Arrastra archivos aquí o haz clic para seleccionar</p>
                <p class="text-xs text-gray-400 mt-1">PDF, DOCX, XLSX (max 80MB cada uno)</p>
              } @else {
                <p class="text-sm font-medium text-primary">{{ selectedFiles().length }} archivo(s) seleccionado(s)</p>
                <p class="text-xs text-gray-500 mt-1">Haz clic para añadir más</p>
              }
            </div>

            <!-- File list -->
            @if (selectedFiles().length > 0) {
              <ul class="mt-3 space-y-1 max-h-36 overflow-y-auto">
                @for (file of selectedFiles(); track file.name; let i = $index) {
                  <li class="flex items-center justify-between text-sm bg-gray-50 rounded-lg px-3 py-1.5">
                    <span class="truncate text-gray-700">{{ file.name }}</span>
                    <span class="text-xs text-gray-400 ml-2 shrink-0">{{ (file.size / 1024 / 1024).toFixed(1) }} MB</span>
                    <button (click)="removeFile(i)" class="ml-2 text-gray-400 hover:text-red-500 shrink-0">
                      <span class="material-icons text-base">close</span>
                    </button>
                  </li>
                }
              </ul>
            }

            <!-- Category (optional) -->
            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Categoría
                <span class="text-gray-400 font-normal">(opcional — se asigna automáticamente si se omite)</span>
              </label>
              <select [(ngModel)]="categoryId"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none text-sm">
                <option value="">Sin categoría (auto-detección)</option>
                @for (cat of categories; track cat.id) {
                  <option [value]="cat.id">{{ cat.name }}</option>
                }
              </select>
            </div>

            <!-- Actions -->
            <div class="mt-6 flex justify-end space-x-3">
              <button (click)="onClose()" class="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg">
                Cancelar
              </button>
              <button (click)="onUpload()" [disabled]="uploading() || selectedFiles().length === 0"
                      class="px-4 py-2 text-sm text-white bg-primary hover:bg-primary-600 rounded-lg disabled:opacity-50">
                @if (uploading()) {
                  Subiendo...
                } @else {
                  Subir {{ fileCount() }} Archivo(s)
                }
              </button>
            </div>
          } @else {
            <!-- Results panel -->
            <p class="text-sm text-gray-600 mb-3">
              {{ successCount() }} de {{ uploadResults().length }} archivo(s) subido(s) exitosamente.
            </p>
            <ul class="space-y-2 max-h-64 overflow-y-auto">
              @for (result of uploadResults(); track result.filename) {
                <li class="flex items-start gap-2 text-sm rounded-lg px-3 py-2"
                    [ngClass]="result.success ? 'bg-green-50' : 'bg-red-50'">
                  <span class="material-icons text-base mt-0.5"
                        [ngClass]="result.success ? 'text-green-500' : 'text-red-500'">
                    {{ result.success ? 'check_circle' : 'error' }}
                  </span>
                  <div class="min-w-0">
                    <p class="font-medium truncate" [ngClass]="result.success ? 'text-green-800' : 'text-red-800'">
                      {{ result.filename }}
                    </p>
                    @if (!result.success && result.error) {
                      <p class="text-xs text-red-600 mt-0.5">{{ result.error }}</p>
                    }
                  </div>
                </li>
              }
            </ul>
            <div class="mt-6 flex justify-end">
              <button (click)="onClose()" class="px-4 py-2 text-sm text-white bg-primary hover:bg-primary-600 rounded-lg">
                Cerrar
              </button>
            </div>
          }
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

  selectedFiles = signal<File[]>([]);
  isDragging = signal(false);
  uploading = signal(false);
  uploadResults = signal<BatchUploadResult[]>([]);
  categoryId = '';

  fileCount = computed(() => this.selectedFiles().length);
  successCount = computed(() => this.uploadResults().filter(r => r.success).length);

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.addFiles(Array.from(input.files));
      // Reset input so the same file can be re-selected after removal
      input.value = '';
    }
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(false);
    if (event.dataTransfer?.files.length) {
      this.addFiles(Array.from(event.dataTransfer.files));
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(true);
  }

  addFiles(newFiles: File[]): void {
    const existing = new Set(this.selectedFiles().map(f => f.name));
    const unique = newFiles.filter(f => !existing.has(f.name));
    this.selectedFiles.set([...this.selectedFiles(), ...unique]);
  }

  removeFile(index: number): void {
    const files = [...this.selectedFiles()];
    files.splice(index, 1);
    this.selectedFiles.set(files);
  }

  onUpload(): void {
    const files = this.selectedFiles();
    if (!files.length) return;

    this.uploading.set(true);
    this.docService.uploadBatch(files, this.categoryId || undefined).subscribe({
      next: (res) => {
        this.uploading.set(false);
        this.uploadResults.set(res.data?.results ?? []);
        const successful = res.data?.successful ?? 0;
        const total = res.data?.total ?? 0;
        if (successful === total) {
          this.toast.success(`${successful} documento(s) subido(s) exitosamente.`);
        } else {
          this.toast.error(`${successful} de ${total} documento(s) subido(s). Revisa los errores.`);
        }
        if (successful > 0) {
          this.uploaded.emit();
        }
      },
      error: (err) => {
        this.uploading.set(false);
        this.toast.error(err.error?.message || 'Error al subir documentos.');
      }
    });
  }

  onClose(): void {
    this.reset();
    this.close.emit();
  }

  private reset(): void {
    this.selectedFiles.set([]);
    this.categoryId = '';
    this.uploadResults.set([]);
    this.isDragging.set(false);
  }
}
