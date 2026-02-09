import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stats-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">{{ label }}</p>
          <p class="text-3xl font-bold mt-1" [style.color]="color">{{ value }}</p>
        </div>
        <div class="w-12 h-12 rounded-lg flex items-center justify-center" [style.background-color]="color + '20'">
          <span class="material-icons text-2xl" [style.color]="color">{{ icon }}</span>
        </div>
      </div>
      @if (subtitle) {
        <p class="text-xs text-gray-400 mt-2">{{ subtitle }}</p>
      }
    </div>
  `,
})
export class StatsCardComponent {
  @Input() label = '';
  @Input() value: string | number = 0;
  @Input() icon = 'info';
  @Input() color = '#1E3A5F';
  @Input() subtitle = '';
}
