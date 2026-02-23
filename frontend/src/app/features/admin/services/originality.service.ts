import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ApiResponse, PaginatedResponse } from '../../../core/models/user.model';
import { ThesisCheck } from '../../../core/models/document.model';

@Injectable({ providedIn: 'root' })
export class OriginalityService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/originality`;

  submit(file: File, scoreThreshold: number): Observable<ApiResponse<{ check: ThesisCheck }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('score_threshold', scoreThreshold.toString());
    return this.http.post<ApiResponse<{ check: ThesisCheck }>>(this.apiUrl, formData);
  }

  list(params?: { page?: number; status?: string }): Observable<PaginatedResponse<ThesisCheck>> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page.toString());
    if (params?.status) httpParams = httpParams.set('status', params.status);
    return this.http.get<PaginatedResponse<ThesisCheck>>(this.apiUrl, { params: httpParams });
  }

  get(id: string): Observable<ApiResponse<{ check: ThesisCheck }>> {
    return this.http.get<ApiResponse<{ check: ThesisCheck }>>(`${this.apiUrl}/${id}`);
  }

  delete(id: string): Observable<ApiResponse<void>> {
    return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
  }
}
