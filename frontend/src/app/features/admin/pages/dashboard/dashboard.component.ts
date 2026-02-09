import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnalyticsService } from '../../services/analytics.service';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { StatsCardComponent } from '../../components/stats-card/stats-card.component';
import { DashboardStats } from '../../../../core/models/document.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, AdminSidebarComponent, StatsCardComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1 p-6 bg-gray-50">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

        <!-- Stats cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <app-stats-card label="Usuarios" [value]="stats()?.total_users ?? 0" icon="people" color="#1E3A5F" />
          <app-stats-card label="Documentos" [value]="stats()?.total_documents ?? 0" icon="description" color="#2E7D32" />
          <app-stats-card label="Conversaciones" [value]="stats()?.total_conversations ?? 0" icon="chat" color="#F57F17" />
          <app-stats-card label="Satisfaccion" [value]="(stats()?.feedback_rate ?? 0) + '%'" icon="thumb_up" color="#C8102E"
                          subtitle="Valoraciones positivas" />
        </div>

        <!-- Usage chart placeholder + Popular queries -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Daily usage -->
          <div class="bg-white rounded-xl shadow-sm border p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Uso Diario (ultimos 30 dias)</h3>
            @if (dailyUsage().length > 0) {
              <div class="space-y-2">
                @for (day of dailyUsage().slice(-10); track day.date) {
                  <div class="flex items-center">
                    <span class="text-xs text-gray-500 w-20">{{ day.date }}</span>
                    <div class="flex-1 bg-gray-100 rounded-full h-4 ml-2">
                      <div class="bg-primary rounded-full h-4 transition-all" [style.width.%]="getBarWidth(day.count)"></div>
                    </div>
                    <span class="text-xs text-gray-600 ml-2 w-8">{{ day.count }}</span>
                  </div>
                }
              </div>
            } @else {
              <p class="text-gray-400 text-sm">Sin datos de uso aun.</p>
            }
          </div>

          <!-- Popular queries -->
          <div class="bg-white rounded-xl shadow-sm border p-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Preguntas Recientes</h3>
            @if (popularQueries().length > 0) {
              <div class="space-y-3">
                @for (q of popularQueries().slice(0, 10); track $index) {
                  <div class="flex items-start space-x-2 text-sm">
                    <span class="material-icons text-primary text-sm mt-0.5">help_outline</span>
                    <span class="text-gray-700">{{ q.content }}</span>
                  </div>
                }
              </div>
            } @else {
              <p class="text-gray-400 text-sm">Sin preguntas registradas aun.</p>
            }
          </div>
        </div>
      </div>
    </div>
  `,
})
export class DashboardComponent implements OnInit {
  private analyticsService = inject(AnalyticsService);

  stats = signal<DashboardStats | null>(null);
  dailyUsage = signal<{ date: string; count: number }[]>([]);
  popularQueries = signal<{ content: string; created_at: string }[]>([]);

  private maxCount = 1;

  ngOnInit(): void {
    this.analyticsService.getDashboard().subscribe({
      next: (res) => this.stats.set(res.data.stats),
    });
    this.analyticsService.getUsage().subscribe({
      next: (res) => {
        this.dailyUsage.set(res.data.daily_usage);
        this.maxCount = Math.max(...res.data.daily_usage.map(d => d.count), 1);
      },
    });
    this.analyticsService.getPopularQueries().subscribe({
      next: (res) => this.popularQueries.set(res.data.popular_queries),
    });
  }

  getBarWidth(count: number): number {
    return Math.max((count / this.maxCount) * 100, 2);
  }
}
