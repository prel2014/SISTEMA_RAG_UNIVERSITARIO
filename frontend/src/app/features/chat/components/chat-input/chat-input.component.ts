import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="border-t bg-white p-4">
      <div class="max-w-4xl mx-auto">
        <form (ngSubmit)="onSend()" class="flex items-end space-x-3">
          <div class="flex-1 relative">
            <textarea
              [(ngModel)]="message"
              name="message"
              [disabled]="disabled"
              (keydown.enter)="onKeyDown($event)"
              placeholder="Escribe tu pregunta sobre la UPAO..."
              rows="1"
              class="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 pr-12 focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors disabled:bg-gray-100"
              [class.opacity-50]="disabled"
              style="min-height: 48px; max-height: 120px;"
            ></textarea>
          </div>
          <button type="submit" [disabled]="disabled || !message.trim()"
                  class="flex-shrink-0 w-12 h-12 bg-primary hover:bg-primary-600 text-white rounded-xl flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            @if (disabled) {
              <span class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
            } @else {
              <span class="material-icons">send</span>
            }
          </button>
        </form>
      </div>
    </div>
  `,
})
export class ChatInputComponent {
  @Input() disabled = false;
  @Output() messageSent = new EventEmitter<string>();

  message = '';

  onSend(): void {
    const text = this.message.trim();
    if (text && !this.disabled) {
      this.messageSent.emit(text);
      this.message = '';
    }
  }

  onKeyDown(event: Event): void {
    const ke = event as KeyboardEvent;
    if (!ke.shiftKey) {
      ke.preventDefault();
      this.onSend();
    }
  }
}
