import { Component, EventEmitter, Input, Output, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../services/chat.service';
import { CategoryFilterComponent } from '../category-filter/category-filter.component';
import { Conversation } from '../../../../core/models/chat.model';

@Component({
  selector: 'app-chat-history-sidebar',
  standalone: true,
  imports: [CommonModule, CategoryFilterComponent],
  template: `
    <div class="w-72 bg-white border-r border-gray-200 flex flex-col h-full">
      <!-- Header -->
      <div class="p-4 border-b">
        <button (click)="newChat.emit()"
                class="w-full flex items-center justify-center px-4 py-2.5 bg-primary hover:bg-primary-600 text-white rounded-lg transition-colors text-sm font-medium">
          <span class="material-icons text-sm mr-2">add</span>
          Nueva conversacion
        </button>
      </div>

      <!-- Category filter -->
      <app-category-filter
        [selectedCategoryId]="selectedCategory"
        (categoryChanged)="categoryChanged.emit($event)" />

      <!-- Conversation list -->
      <div class="flex-1 overflow-y-auto">
        @if (conversations().length === 0) {
          <div class="p-4 text-center text-sm text-gray-400">
            No hay conversaciones
          </div>
        }
        @for (conv of conversations(); track conv.conversation_id) {
          <button (click)="conversationSelected.emit(conv.conversation_id)"
                  class="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 transition-colors"
                  [ngClass]="conv.conversation_id === activeConversationId ? 'bg-primary-50 border-l-2 border-l-primary' : ''">
            <p class="text-sm text-gray-800 truncate">{{ conv.preview || 'Conversacion' }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ formatDate(conv.last_message_at) }}</p>
          </button>
        }
      </div>
    </div>
  `,
})
export class ChatHistorySidebarComponent implements OnInit {
  @Input() activeConversationId = '';
  @Input() selectedCategory = '';
  @Output() conversationSelected = new EventEmitter<string>();
  @Output() newChat = new EventEmitter<void>();
  @Output() categoryChanged = new EventEmitter<string>();

  private chatService = inject(ChatService);
  conversations = signal<Conversation[]>([]);

  ngOnInit(): void {
    this.loadConversations();
  }

  loadConversations(): void {
    this.chatService.getConversations().subscribe({
      next: (res) => this.conversations.set(res.data),
    });
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('es-PE', { day: '2-digit', month: 'short' });
  }
}
