import { Component, Injectable, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  toasts = signal<Toast[]>([]);
  private nextId = 0;

  show(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    const id = this.nextId++;
    this.toasts.update(t => [...t, { id, message, type }]);
    setTimeout(() => this.remove(id), 4000);
  }

  success(message: string): void { this.show(message, 'success'); }
  error(message: string): void { this.show(message, 'error'); }
  info(message: string): void { this.show(message, 'info'); }

  remove(id: number): void {
    this.toasts.update(t => t.filter(toast => toast.id !== id));
  }
}

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="fixed top-4 right-4 z-50 space-y-2">
      @for (toast of toastService.toasts(); track toast.id) {
        <div class="flex items-center px-4 py-3 rounded-lg shadow-lg text-white min-w-[300px] animate-slide-in"
             [ngClass]="{
               'bg-green-600': toast.type === 'success',
               'bg-red-600': toast.type === 'error',
               'bg-blue-600': toast.type === 'info'
             }">
          <span class="material-icons text-sm mr-2">
            {{ toast.type === 'success' ? 'check_circle' : toast.type === 'error' ? 'error' : 'info' }}
          </span>
          <span class="flex-1 text-sm">{{ toast.message }}</span>
          <button (click)="toastService.remove(toast.id)" class="ml-2 hover:opacity-75">
            <span class="material-icons text-sm">close</span>
          </button>
        </div>
      }
    </div>
  `,
  styles: [`
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    .animate-slide-in { animation: slideIn 0.3s ease-out; }
  `]
})
export class ToastComponent {
  constructor(public toastService: ToastService) {}
}
