import { Component, EventEmitter, Input, Output, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import { Category } from '../../../../core/models/document.model';
import { ApiResponse } from '../../../../core/models/user.model';

@Component({
  selector: 'app-category-filter',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="px-3 py-2">
      <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">Filtrar por categoria</label>
      <select (change)="onCategoryChange($event)"
              class="mt-1 w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-primary outline-none">
        <option value="">Todas las categorias</option>
        @for (cat of categories(); track cat.id) {
          <option [value]="cat.id" [selected]="cat.id === selectedCategoryId">
            {{ cat.name }}
          </option>
        }
      </select>
    </div>
  `,
})
export class CategoryFilterComponent implements OnInit {
  @Input() selectedCategoryId = '';
  @Output() categoryChanged = new EventEmitter<string>();
  private http = inject(HttpClient);

  categories = signal<Category[]>([]);

  ngOnInit(): void {
    this.http.get<ApiResponse<{ categories: Category[] }>>(`${environment.apiUrl}/categories`).subscribe({
      next: (res) => this.categories.set(res.data.categories),
    });
  }

  onCategoryChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.categoryChanged.emit(value);
  }
}
