import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatMessage } from '../../../../core/models/chat.model';
import { SourcePanelComponent } from '../source-panel/source-panel.component';
import { FeedbackButtonsComponent } from '../feedback-buttons/feedback-buttons.component';

@Component({
  selector: 'app-message-bubble',
  standalone: true,
  imports: [CommonModule, SourcePanelComponent, FeedbackButtonsComponent],
  template: `
    <div class="flex mb-4" [ngClass]="message.role === 'user' ? 'justify-end' : 'justify-start'">
      <div class="max-w-[80%]">
        <!-- Avatar + Message -->
        <div class="flex items-start space-x-2" [ngClass]="message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''">
          <!-- Avatar -->
          <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm"
               [ngClass]="message.role === 'user' ? 'bg-primary' : 'bg-secondary'">
            <span class="material-icons text-sm">
              {{ message.role === 'user' ? 'person' : 'smart_toy' }}
            </span>
          </div>

          <!-- Bubble -->
          <div class="rounded-2xl px-4 py-3 shadow-sm"
               [ngClass]="message.role === 'user'
                 ? 'bg-primary text-white rounded-tr-sm'
                 : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'">
            <div class="markdown-content text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</div>
          </div>
        </div>

        <!-- Sources + Feedback (assistant only) -->
        @if (message.role === 'assistant') {
          <div class="ml-10 mt-2 space-y-2">
            @if (message.source_documents && message.source_documents.length > 0) {
              <app-source-panel [sources]="message.source_documents" />
            }
            <app-feedback-buttons [messageId]="message.id" />
          </div>
        }

        <!-- Timestamp -->
        <div class="text-xs text-gray-400 mt-1" [ngClass]="message.role === 'user' ? 'text-right mr-10' : 'ml-10'">
          {{ formatTime(message.created_at) }}
        </div>
      </div>
    </div>
  `,
})
export class MessageBubbleComponent {
  @Input() message!: ChatMessage;

  formatTime(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' });
  }
}
