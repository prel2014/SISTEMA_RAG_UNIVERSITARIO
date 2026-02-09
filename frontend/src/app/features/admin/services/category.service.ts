import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ApiResponse } from '../../../core/models/user.model';
import { Category } from '../../../core/models/document.model';

@Injectable({ providedIn: 'root' })
export class CategoryService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/categories`;

  listAll(): Observable<ApiResponse<{ categories: Category[] }>> {
    return this.http.get<ApiResponse<{ categories: Category[] }>>(`${this.apiUrl}/all`);
  }

  list(): Observable<ApiResponse<{ categories: Category[] }>> {
    return this.http.get<ApiResponse<{ categories: Category[] }>>(this.apiUrl);
  }

  create(data: { name: string; description?: string; icon?: string; color?: string }): Observable<ApiResponse<{ category: Category }>> {
    return this.http.post<ApiResponse<{ category: Category }>>(this.apiUrl, data);
  }

  update(id: string, data: Partial<Category>): Observable<ApiResponse<{ category: Category }>> {
    return this.http.put<ApiResponse<{ category: Category }>>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<ApiResponse<void>> {
    return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
  }
}
