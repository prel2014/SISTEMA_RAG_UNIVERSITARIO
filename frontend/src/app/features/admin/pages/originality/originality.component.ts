import { Component, inject, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';
import { ConfirmDialogComponent } from '../../../../shared/components/confirm-dialog/confirm-dialog.component';
import { ToastService } from '../../../../shared/components/toast/toast.component';
import { OriginalityService } from '../../services/originality.service';
import { ThesisCheck, ThesisMatchDocument } from '../../../../core/models/document.model';
import { PAGE_SIZE } from '../../../../shared/constants/pagination';
import { getStatusLabel, getStatusBadgeClass } from '../../../../shared/utils/status.utils';
import { scoreColorClass, levelBadgeClass, levelLabel } from '../../../../shared/utils/originality.utils';

@Component({
  selector: 'app-originality',
  standalone: true,
  imports: [CommonModule, FormsModule, AdminSidebarComponent, PaginationComponent, ConfirmDialogComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1 p-6 bg-gray-50 min-h-screen">

        <!-- ===== REPORT VIEW ===== -->
        @if (selectedCheck()) {
          <div>
            <button (click)="selectedCheck.set(null)"
                    class="flex items-center text-sm text-primary hover:underline mb-4">
              <span class="material-icons text-base mr-1">arrow_back</span>
              Volver a la lista
            </button>

            <h1 class="text-2xl font-bold text-gray-800 mb-1">Reporte de Originalidad</h1>
            <p class="text-sm text-gray-500 mb-6">{{ selectedCheck()!.filename }}</p>

            <!-- Summary cards -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
                <div class="text-3xl font-bold" [ngClass]="scoreColorClass(selectedCheck()!.originality_score)">
                  {{ selectedCheck()!.originality_score !== null ? (selectedCheck()!.originality_score | number:'1.1-1') + '%' : '-' }}
                </div>
                <div class="text-xs text-gray-500 mt-1">Originalidad</div>
              </div>
              <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
                <div class="text-xl font-semibold mt-1">
                  <span class="px-3 py-1 rounded-full text-sm font-medium"
                        [ngClass]="levelBadgeClass(selectedCheck()!.plagiarism_level)">
                    {{ levelLabel(selectedCheck()!.plagiarism_level) }}
                  </span>
                </div>
                <div class="text-xs text-gray-500 mt-2">Nivel de Plagio</div>
              </div>
              <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
                <div class="text-3xl font-bold text-gray-700">{{ selectedCheck()!.total_chunks }}</div>
                <div class="text-xs text-gray-500 mt-1">Total Chunks</div>
              </div>
              <div class="bg-white rounded-xl shadow-sm border p-4 text-center">
                <div class="text-3xl font-bold text-red-500">{{ selectedCheck()!.flagged_chunks }}</div>
                <div class="text-xs text-gray-500 mt-1">Chunks Marcados</div>
              </div>
            </div>

            <!-- Progress bar -->
            <div class="bg-white rounded-xl shadow-sm border p-4 mb-6">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Plagio detectado</span>
                <span>Original</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden flex">
                <div class="h-4 bg-red-400 transition-all duration-500"
                     [style.width.%]="100 - (selectedCheck()!.originality_score ?? 100)"></div>
                <div class="h-4 bg-green-400 transition-all duration-500"
                     [style.width.%]="selectedCheck()!.originality_score ?? 100"></div>
              </div>
              <div class="flex justify-between text-xs text-gray-400 mt-1">
                <span>{{ (100 - (selectedCheck()!.originality_score ?? 100)) | number:'1.1-1' }}%</span>
                <span>{{ (selectedCheck()!.originality_score ?? 100) | number:'1.1-1' }}%</span>
              </div>
            </div>

            <!-- Matched documents table -->
            @if (selectedCheck()!.matches_summary && selectedCheck()!.matches_summary!.documents.length > 0) {
              <div class="bg-white rounded-xl shadow-sm border overflow-hidden mb-6">
                <div class="px-4 py-3 border-b bg-gray-50">
                  <h2 class="text-sm font-semibold text-gray-700">
                    Documentos Similares ({{ selectedCheck()!.matches_summary!.total_documents_matched }} encontrados)
                  </h2>
                </div>
                <table class="w-full">
                  <thead class="bg-gray-50 border-b">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Documento</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Similitud %</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score Maximo</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunks</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nivel</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Paginas</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Analisis LLM</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y">
                    @for (doc of selectedCheck()!.matches_summary!.documents; track doc.document_id) {
                      <tr class="hover:bg-gray-50">
                        <td class="px-4 py-3 max-w-xs">
                          <div class="text-sm font-medium text-gray-900 truncate" [title]="doc.title">{{ doc.title }}</div>
                          @if (doc.common_themes.length) {
                            <div class="flex flex-wrap gap-1 mt-1">
                              @for (theme of doc.common_themes; track theme) {
                                <span class="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">{{ theme }}</span>
                              }
                            </div>
                          }
                          @if (doc.technologies.length) {
                            <div class="flex flex-wrap gap-1 mt-1">
                              @for (tech of doc.technologies; track tech) {
                                <span class="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 rounded">{{ tech }}</span>
                              }
                            </div>
                          }
                          @if (doc.methods.length) {
                            <div class="flex flex-wrap gap-1 mt-1">
                              @for (method of doc.methods; track method) {
                                <span class="text-xs px-1.5 py-0.5 bg-violet-100 text-violet-700 rounded">{{ method }}</span>
                              }
                            </div>
                          }
                        </td>
                        <td class="px-4 py-3">
                          <div class="flex items-center gap-2">
                            <div class="flex-1 bg-gray-100 rounded-full h-2 max-w-24">
                              <div class="h-2 rounded-full bg-red-400" [style.width.%]="doc.similarity_pct"></div>
                            </div>
                            <span class="text-sm font-medium text-gray-700">{{ doc.similarity_pct | number:'1.1-1' }}%</span>
                          </div>
                        </td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ doc.max_score | number:'1.3-3' }}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">{{ doc.chunk_hits }}</td>
                        <td class="px-4 py-3">
                          <span class="text-xs font-medium px-2 py-1 rounded-full"
                                [ngClass]="levelBadgeClass(doc.risk_level)">
                            {{ levelLabel(doc.risk_level) }}
                          </span>
                        </td>
                        <td class="px-4 py-3 text-xs text-gray-500">{{ doc.pages_hit.slice(0,8).join(', ') }}{{ doc.pages_hit.length > 8 ? '...' : '' }}</td>
                        <td class="px-4 py-3">
                          @if (doc.llm_analysis || doc.approach || doc.problem_overlap) {
                            <div>
                              <button (click)="toggleExpand(doc.document_id)"
                                      class="text-xs text-primary underline hover:no-underline">
                                {{ expandedDocs().has(doc.document_id) ? 'Ocultar' : 'Ver análisis' }}
                              </button>
                              @if (expandedDocs().has(doc.document_id)) {
                                <div class="text-xs text-gray-600 mt-1 max-w-sm space-y-1.5 leading-relaxed">
                                  @if (doc.approach) {
                                    <p><span class="font-medium text-gray-700">Enfoque: </span>{{ doc.approach }}</p>
                                  }
                                  @if (doc.problem_overlap) {
                                    <p><span class="font-medium text-gray-700">Problema común: </span>{{ doc.problem_overlap }}</p>
                                  }
                                  @if (doc.llm_analysis) {
                                    <p>{{ doc.llm_analysis }}</p>
                                  }
                                </div>
                              }
                            </div>
                          } @else {
                            <span class="text-xs text-gray-300">—</span>
                          }
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            } @else {
              <div class="bg-white rounded-xl shadow-sm border p-8 text-center text-gray-400">
                No se encontraron documentos similares en la base de datos.
              </div>
            }

            <!-- Threshold legend -->
            <div class="bg-white rounded-xl shadow-sm border p-4">
              <h3 class="text-xs font-semibold text-gray-500 uppercase mb-3">Leyenda de Umbrales (umbral usado: {{ selectedCheck()!.score_threshold | number:'1.2-2' }})</h3>
              <div class="flex flex-wrap gap-3">
                <span class="flex items-center gap-1 text-xs"><span class="w-3 h-3 rounded-full bg-green-400 inline-block"></span> Bajo (&lt; 50%)</span>
                <span class="flex items-center gap-1 text-xs"><span class="w-3 h-3 rounded-full bg-yellow-400 inline-block"></span> Moderado (50–65%)</span>
                <span class="flex items-center gap-1 text-xs"><span class="w-3 h-3 rounded-full bg-orange-400 inline-block"></span> Alto (65–85%)</span>
                <span class="flex items-center gap-1 text-xs"><span class="w-3 h-3 rounded-full bg-red-500 inline-block"></span> Muy Alto (&ge; 85%)</span>
              </div>
            </div>
          </div>
        }

        <!-- ===== LIST VIEW ===== -->
        @if (!selectedCheck()) {
          <div>
            <div class="flex items-center justify-between mb-6">
              <h1 class="text-2xl font-bold text-gray-800">Verificacion de Originalidad de Tesis</h1>
              <button (click)="showUpload.set(true)"
                      class="px-4 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors">
                <span class="material-icons text-sm align-middle mr-1">upload_file</span>
                Nueva Verificacion
              </button>
            </div>

            <!-- Filter -->
            <div class="bg-white rounded-xl shadow-sm border p-4 mb-4 flex gap-4">
              <select [(ngModel)]="filterStatus" (change)="loadChecks()"
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
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Archivo</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Puntaje</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nivel</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Umbral</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody class="divide-y">
                  @for (check of checks(); track check.id) {
                    <tr class="hover:bg-gray-50">
                      <td class="px-4 py-3">
                        <div class="text-sm font-medium text-gray-900 max-w-xs truncate" [title]="check.filename">{{ check.filename }}</div>
                      </td>
                      <td class="px-4 py-3">
                        <span class="text-xs font-medium px-2 py-1 bg-gray-100 rounded uppercase">{{ check.file_type }}</span>
                      </td>
                      <td class="px-4 py-3">
                        <span class="text-xs font-medium px-2 py-1 rounded-full"
                              [ngClass]="getStatusBadgeClass(check.status)">
                          {{ getStatusLabel(check.status) }}
                        </span>
                      </td>
                      <td class="px-4 py-3">
                        @if (check.originality_score !== null) {
                          <span class="text-sm font-semibold" [ngClass]="scoreColorClass(check.originality_score)">
                            {{ check.originality_score | number:'1.1-1' }}%
                          </span>
                        } @else {
                          <span class="text-sm text-gray-400">-</span>
                        }
                      </td>
                      <td class="px-4 py-3">
                        @if (check.plagiarism_level) {
                          <span class="text-xs font-medium px-2 py-1 rounded-full"
                                [ngClass]="levelBadgeClass(check.plagiarism_level)">
                            {{ levelLabel(check.plagiarism_level) }}
                          </span>
                        } @else {
                          <span class="text-sm text-gray-400">-</span>
                        }
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-500">{{ check.score_threshold | number:'1.2-2' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-500">{{ check.created_at | date:'dd/MM/yy HH:mm' }}</td>
                      <td class="px-4 py-3">
                        <div class="flex space-x-1">
                          @if (check.status === 'completed') {
                            <button (click)="viewReport(check.id)" title="Ver Reporte"
                                    class="p-1 text-gray-400 hover:text-primary rounded">
                              <span class="material-icons text-sm">visibility</span>
                            </button>
                          }
                          <button (click)="deleteId.set(check.id)" title="Eliminar"
                                  class="p-1 text-gray-400 hover:text-red-600 rounded">
                            <span class="material-icons text-sm">delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  } @empty {
                    <tr>
                      <td colspan="8" class="px-4 py-8 text-center text-gray-400">No hay verificaciones.</td>
                    </tr>
                  }
                </tbody>
              </table>
              <app-pagination [total]="total()" [currentPage]="currentPage" [perPage]="PAGE_SIZE"
                              (pageChange)="onPageChange($event)" />
            </div>

            <!-- Confirm delete -->
            <app-confirm-dialog [isOpen]="!!deleteId()" title="Eliminar Verificacion"
                                message="Esta seguro de eliminar esta verificacion? Esta accion no se puede deshacer."
                                confirmText="Eliminar"
                                (confirmed)="confirmDeleteCheck()" (cancelled)="deleteId.set('')" />

            <!-- Upload modal -->
            @if (showUpload()) {
              <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
                  <h2 class="text-lg font-bold text-gray-800 mb-4">Nueva Verificacion de Tesis</h2>

                  <!-- Drop zone -->
                  <div class="border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer mb-4"
                       [ngClass]="isDragging() ? 'border-primary bg-primary-50' : 'border-gray-300 hover:border-primary'"
                       (dragover)="onDragOver($event)" (dragleave)="isDragging.set(false)" (drop)="onDrop($event)"
                       (click)="fileInput.click()">
                    @if (selectedFile()) {
                      <div>
                        <span class="material-icons text-3xl text-green-500">check_circle</span>
                        <p class="text-sm font-medium text-gray-700 mt-1">{{ selectedFile()!.name }}</p>
                        <p class="text-xs text-gray-400">{{ (selectedFile()!.size / 1024 / 1024) | number:'1.1-1' }} MB</p>
                      </div>
                    } @else {
                      <span class="material-icons text-3xl text-gray-400">upload_file</span>
                      <p class="text-sm text-gray-500 mt-1">Arrastra o haz clic para seleccionar</p>
                      <p class="text-xs text-gray-400">PDF, DOCX, TXT — max 50 MB</p>
                    }
                    <input #fileInput type="file" accept=".pdf,.docx,.txt" class="hidden" (change)="onFileSelect($event)" />
                  </div>

                  <!-- Threshold -->
                  <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Umbral de similitud ({{ scoreThreshold | number:'1.2-2' }})
                    </label>
                    <input type="range" min="0.50" max="0.95" step="0.05" [(ngModel)]="scoreThreshold"
                           class="w-full accent-primary" />
                    <div class="flex justify-between text-xs text-gray-400 mt-0.5">
                      <span>0.50 (mas sensible)</span>
                      <span>0.95 (mas estricto)</span>
                    </div>
                  </div>

                  <div class="flex justify-end gap-3">
                    <button (click)="closeUpload()"
                            class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                      Cancelar
                    </button>
                    <button (click)="submitCheck()" [disabled]="!selectedFile() || uploading()"
                            class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
                      @if (uploading()) {
                        <span class="material-icons text-sm animate-spin">refresh</span>
                      }
                      Verificar
                    </button>
                  </div>
                </div>
              </div>
            }
          </div>
        }

      </div>
    </div>
  `,
})
export class OriginalityComponent implements OnInit, OnDestroy {
  private svc = inject(OriginalityService);
  private toast = inject(ToastService);

  readonly PAGE_SIZE = PAGE_SIZE;
  readonly getStatusLabel = getStatusLabel;
  readonly getStatusBadgeClass = getStatusBadgeClass;
  readonly scoreColorClass = scoreColorClass;
  readonly levelBadgeClass = levelBadgeClass;
  readonly levelLabel = levelLabel;

  checks = signal<ThesisCheck[]>([]);
  total = signal(0);
  selectedCheck = signal<ThesisCheck | null>(null);
  showUpload = signal(false);
  selectedFile = signal<File | null>(null);
  isDragging = signal(false);
  uploading = signal(false);
  deleteId = signal('');
  expandedDocs = signal<Set<string>>(new Set());

  filterStatus = '';
  currentPage = 1;
  scoreThreshold = 0.70;

  private pollInterval: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.loadChecks();
    this.startPolling();
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  loadChecks(): void {
    this.svc.list({ page: this.currentPage, status: this.filterStatus }).subscribe({
      next: (res) => {
        this.checks.set(res.data);
        this.total.set(res.pagination.total);
        this.managePolling();
      },
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadChecks();
  }

  viewReport(id: string): void {
    this.svc.get(id).subscribe({
      next: (res) => {
        this.selectedCheck.set(res.data['check']);
        this.expandedDocs.set(new Set());
      },
      error: () => this.toast.error('Error al cargar el reporte.'),
    });
  }

  toggleExpand(docId: string): void {
    const current = new Set(this.expandedDocs());
    if (current.has(docId)) {
      current.delete(docId);
    } else {
      current.add(docId);
    }
    this.expandedDocs.set(current);
  }

  confirmDeleteCheck(): void {
    const id = this.deleteId();
    if (!id) return;
    this.svc.delete(id).subscribe({
      next: () => {
        this.toast.success('Verificacion eliminada.');
        this.deleteId.set('');
        if (this.selectedCheck()?.id === id) this.selectedCheck.set(null);
        this.loadChecks();
      },
      error: () => this.toast.error('Error al eliminar la verificacion.'),
    });
  }

  submitCheck(): void {
    const file = this.selectedFile();
    if (!file) return;
    this.uploading.set(true);
    this.svc.submit(file, this.scoreThreshold).subscribe({
      next: () => {
        this.toast.success('Verificacion iniciada.');
        this.closeUpload();
        this.loadChecks();
      },
      error: (err) => {
        this.toast.error(err?.error?.message || 'Error al enviar el archivo.');
        this.uploading.set(false);
      },
    });
  }

  closeUpload(): void {
    this.showUpload.set(false);
    this.selectedFile.set(null);
    this.isDragging.set(false);
    this.uploading.set(false);
  }

  onFileSelect(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) this.selectedFile.set(input.files[0]);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(true);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging.set(false);
    const file = event.dataTransfer?.files[0];
    if (file) this.selectedFile.set(file);
  }

  private managePolling(): void {
    const hasActive = this.checks().some(c => c.status === 'pending' || c.status === 'processing');
    if (hasActive) {
      this.startPolling();
    } else {
      this.stopPolling();
    }
  }

  private startPolling(): void {
    if (this.pollInterval) return;
    this.pollInterval = setInterval(() => this.loadChecks(), 5000);
  }

  private stopPolling(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
  }
}
