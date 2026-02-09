import { Component, Input, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-feedback-buttons',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="flex items-center space-x-1">
      <button (click)="submitFeedback(1)" [disabled]="submitted()"
              class="p-1 rounded hover:bg-gray-100 transition-colors"
              [ngClass]="currentRating() === 1 ? 'text-green-600' : 'text-gray-400'">
        <span class="material-icons text-sm">thumb_up</span>
      </button>
      <button (click)="submitFeedback(-1)" [disabled]="submitted()"
              class="p-1 rounded hover:bg-gray-100 transition-colors"
              [ngClass]="currentRating() === -1 ? 'text-red-600' : 'text-gray-400'">
        <span class="material-icons text-sm">thumb_down</span>
      </button>
      @if (submitted()) {
        <span class="text-xs text-gray-400 ml-1">Gracias</span>
      }
    </div>
  `,
})
export class FeedbackButtonsComponent {
  @Input() messageId!: string;
  private chatService = inject(ChatService);

  currentRating = signal<number | null>(null);
  submitted = signal(false);

  submitFeedback(rating: 1 | -1): void {
    if (this.submitted()) return;
    this.currentRating.set(rating);
    this.submitted.set(true);
    this.chatService.sendFeedback(this.messageId, rating).subscribe();
  }
}
