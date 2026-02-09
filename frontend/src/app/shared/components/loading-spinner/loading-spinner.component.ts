import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="flex items-center justify-center" [class]="containerClass">
      <div class="animate-spin rounded-full border-4 border-primary-200 border-t-primary"
           [ngClass]="{'h-8 w-8': size === 'md', 'h-5 w-5': size === 'sm', 'h-12 w-12': size === 'lg'}">
      </div>
      @if (message) {
        <span class="ml-3 text-gray-600">{{ message }}</span>
      }
    </div>
  `,
})
export class LoadingSpinnerComponent {
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() message = '';
  @Input() containerClass = 'py-8';
}
