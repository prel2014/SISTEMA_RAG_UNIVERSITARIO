import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (totalPages > 1) {
      <div class="flex items-center justify-between px-4 py-3">
        <p class="text-sm text-gray-700">
          Mostrando <span class="font-medium">{{ (currentPage - 1) * perPage + 1 }}</span>
          a <span class="font-medium">{{ Math.min(currentPage * perPage, total) }}</span>
          de <span class="font-medium">{{ total }}</span> resultados
        </p>
        <div class="flex space-x-1">
          <button (click)="goToPage(currentPage - 1)" [disabled]="currentPage === 1"
                  class="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            Anterior
          </button>
          @for (page of visiblePages; track page) {
            <button (click)="goToPage(page)"
                    class="px-3 py-1 text-sm border rounded"
                    [ngClass]="page === currentPage ? 'bg-primary text-white' : 'hover:bg-gray-50'">
              {{ page }}
            </button>
          }
          <button (click)="goToPage(currentPage + 1)" [disabled]="currentPage === totalPages"
                  class="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            Siguiente
          </button>
        </div>
      </div>
    }
  `,
})
export class PaginationComponent {
  @Input() total = 0;
  @Input() currentPage = 1;
  @Input() perPage = 20;
  @Output() pageChange = new EventEmitter<number>();

  Math = Math;

  get totalPages(): number {
    return Math.ceil(this.total / this.perPage);
  }

  get visiblePages(): number[] {
    const pages: number[] = [];
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, start + 4);
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.pageChange.emit(page);
    }
  }
}
