import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ApiResponse, PaginatedResponse } from '../../../core/models/user.model';
import { Document, BatchUploadData } from '../../../core/models/document.model';

@Injectable({ providedIn: 'root' })
export class DocumentService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/documents`;

  list(params?: { page?: number; search?: string; category_id?: string; status?: string }): Observable<PaginatedResponse<Document>> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page.toString());
    if (params?.search) httpParams = httpParams.set('search', params.search);
    if (params?.category_id) httpParams = httpParams.set('category_id', params.category_id);
    if (params?.status) httpParams = httpParams.set('status', params.status);
    return this.http.get<PaginatedResponse<Document>>(this.apiUrl, { params: httpParams });
  }

  get(id: string): Observable<ApiResponse<{ document: Document }>> {
    return this.http.get<ApiResponse<{ document: Document }>>(`${this.apiUrl}/${id}`);
  }

  upload(file: File, title: string, categoryId?: string): Observable<ApiResponse<{ document: Document }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (categoryId) formData.append('category_id', categoryId);
    return this.http.post<ApiResponse<{ document: Document }>>(`${this.apiUrl}/upload`, formData);
  }

  update(id: string, data: { title?: string; category_id?: string }): Observable<ApiResponse<{ document: Document }>> {
    return this.http.put<ApiResponse<{ document: Document }>>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<ApiResponse<void>> {
    return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
  }

  reprocess(id: string): Observable<ApiResponse<{ document: Document }>> {
    return this.http.post<ApiResponse<{ document: Document }>>(`${this.apiUrl}/${id}/reprocess`, {});
  }

  uploadBatch(files: File[], categoryId?: string): Observable<ApiResponse<BatchUploadData>> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    if (categoryId) formData.append('category_id', categoryId);
    return this.http.post<ApiResponse<BatchUploadData>>(`${this.apiUrl}/upload-batch`, formData);
  }
}
