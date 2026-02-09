import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RagConfigService } from '../../services/rag-config.service';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { ToastService } from '../../../../shared/components/toast/toast.component';
import { RagConfig } from '../../../../core/models/document.model';

@Component({
  selector: 'app-rag-config',
  standalone: true,
  imports: [CommonModule, FormsModule, AdminSidebarComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1 p-6 bg-gray-50">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Configuracion RAG</h1>

        @if (config()) {
          <div class="max-w-2xl">
            <div class="bg-white rounded-xl shadow-sm border p-6 space-y-6">
              <!-- Read-only info -->
              <div class="bg-gray-50 rounded-lg p-4">
                <h3 class="text-sm font-medium text-gray-700 mb-2">Modelos (solo lectura)</h3>
                <p class="text-sm text-gray-600">LLM: <span class="font-mono">{{ config()!.llm_model }}</span></p>
                <p class="text-sm text-gray-600">Embeddings: <span class="font-mono">{{ config()!.embedding_model }}</span></p>
              </div>

              <!-- Editable fields -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Tamano de chunk</label>
                  <input type="number" [(ngModel)]="form.chunk_size" min="100" max="5000"
                         class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Overlap de chunk</label>
                  <input type="number" [(ngModel)]="form.chunk_overlap" min="0" max="1000"
                         class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Top K resultados</label>
                  <input type="number" [(ngModel)]="form.top_k" min="1" max="20"
                         class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Umbral de similitud</label>
                  <input type="number" [(ngModel)]="form.score_threshold" min="0" max="1" step="0.05"
                         class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Temperatura</label>
                  <input type="number" [(ngModel)]="form.temperature" min="0" max="1" step="0.1"
                         class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Contexto (tokens)</label>
                  <input type="number" [(ngModel)]="form.num_ctx" min="1024" max="32768" step="1024"
                         class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none">
                </div>
              </div>

              <button (click)="saveConfig()" [disabled]="saving()"
                      class="px-6 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg text-sm font-medium disabled:opacity-50">
                {{ saving() ? 'Guardando...' : 'Guardar Configuracion' }}
              </button>
            </div>
          </div>
        }
      </div>
    </div>
  `,
})
export class RagConfigComponent implements OnInit {
  private ragConfigService = inject(RagConfigService);
  private toast = inject(ToastService);

  config = signal<RagConfig | null>(null);
  saving = signal(false);

  form = {
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 5,
    score_threshold: 0.35,
    temperature: 0.3,
    num_ctx: 4096,
  };

  ngOnInit(): void {
    this.ragConfigService.get().subscribe({
      next: (res) => {
        this.config.set(res.data.config);
        const c = res.data.config;
        this.form = {
          chunk_size: c.chunk_size,
          chunk_overlap: c.chunk_overlap,
          top_k: c.top_k,
          score_threshold: c.score_threshold,
          temperature: c.temperature,
          num_ctx: c.num_ctx,
        };
      }
    });
  }

  saveConfig(): void {
    this.saving.set(true);
    this.ragConfigService.update(this.form).subscribe({
      next: (res) => {
        this.saving.set(false);
        this.config.set(res.data.config);
        this.toast.success('Configuracion guardada exitosamente.');
      },
      error: (err) => {
        this.saving.set(false);
        this.toast.error(err.error?.message || 'Error al guardar configuracion.');
      }
    });
  }
}
