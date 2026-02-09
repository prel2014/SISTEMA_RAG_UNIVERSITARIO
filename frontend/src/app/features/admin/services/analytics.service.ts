import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { ApiResponse } from '../../../core/models/user.model';
import { DashboardStats } from '../../../core/models/document.model';

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/analytics`;

  getDashboard(): Observable<ApiResponse<{ stats: DashboardStats }>> {
    return this.http.get<ApiResponse<{ stats: DashboardStats }>>(`${this.apiUrl}/dashboard`);
  }

  getUsage(): Observable<ApiResponse<{ daily_usage: { date: string; count: number }[] }>> {
    return this.http.get<ApiResponse<{ daily_usage: { date: string; count: number }[] }>>(`${this.apiUrl}/usage`);
  }

  getPopularQueries(): Observable<ApiResponse<{ popular_queries: { content: string; created_at: string }[] }>> {
    return this.http.get<ApiResponse<{ popular_queries: { content: string; created_at: string }[] }>>(`${this.apiUrl}/popular-queries`);
  }

  getFeedbackSummary(): Observable<ApiResponse<{ summary: any; recent_negative: any[] }>> {
    return this.http.get<ApiResponse<{ summary: any; recent_negative: any[] }>>(`${this.apiUrl}/feedback-summary`);
  }
}
