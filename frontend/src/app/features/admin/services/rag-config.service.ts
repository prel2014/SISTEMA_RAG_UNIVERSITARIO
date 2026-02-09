import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ApiResponse } from '../../../core/models/user.model';
import { RagConfig } from '../../../core/models/document.model';

@Injectable({ providedIn: 'root' })
export class RagConfigService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/config/rag`;

  get(): Observable<ApiResponse<{ config: RagConfig }>> {
    return this.http.get<ApiResponse<{ config: RagConfig }>>(this.apiUrl);
  }

  update(data: Partial<RagConfig>): Observable<ApiResponse<{ config: RagConfig }>> {
    return this.http.put<ApiResponse<{ config: RagConfig }>>(this.apiUrl, data);
  }
}
