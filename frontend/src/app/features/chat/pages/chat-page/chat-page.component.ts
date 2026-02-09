import { Component, inject, signal, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../services/chat.service';
import { ChatMessage, SourceDocument } from '../../../../core/models/chat.model';
import { AuthService } from '../../../../core/services/auth.service';
import { MessageBubbleComponent } from '../../components/message-bubble/message-bubble.component';
import { ChatInputComponent } from '../../components/chat-input/chat-input.component';
import { SuggestionChipsComponent } from '../../components/suggestion-chips/suggestion-chips.component';
import { ChatHistorySidebarComponent } from '../../components/chat-history-sidebar/chat-history-sidebar.component';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [
    CommonModule,
    MessageBubbleComponent,
    ChatInputComponent,
    SuggestionChipsComponent,
    ChatHistorySidebarComponent,
  ],
  template: `
    <div class="flex h-[calc(100vh-4rem)]">
      <!-- Sidebar -->
      <app-chat-history-sidebar
        [activeConversationId]="conversationId()"
        [selectedCategory]="selectedCategory()"
        (conversationSelected)="loadConversation($event)"
        (newChat)="startNewChat()"
        (categoryChanged)="selectedCategory.set($event)" />

      <!-- Chat area -->
      <div class="flex-1 flex flex-col">
        <!-- Messages -->
        <div #messagesContainer class="flex-1 overflow-y-auto px-4 py-6">
          <div class="max-w-4xl mx-auto">
            @if (messages().length === 0 && !isStreaming()) {
              <app-suggestion-chips (selected)="onSendMessage($event)" />
            } @else {
              @for (msg of messages(); track msg.id || $index) {
                <app-message-bubble [message]="msg" />
              }

              <!-- Streaming message -->
              @if (isStreaming()) {
                <div class="flex justify-start mb-4">
                  <div class="max-w-[80%]">
                    <div class="flex items-start space-x-2">
                      <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-secondary text-white text-sm">
                        <span class="material-icons text-sm">smart_toy</span>
                      </div>
                      <div class="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                        <div class="text-sm leading-relaxed whitespace-pre-wrap">
                          {{ streamingContent() }}
                          <span class="inline-block w-2 h-4 bg-primary animate-pulse ml-0.5"></span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              }
            }
          </div>
        </div>

        <!-- Input -->
        <app-chat-input [disabled]="isStreaming()" (messageSent)="onSendMessage($event)" />
      </div>
    </div>
  `,
})
export class ChatPageComponent implements AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  private chatService = inject(ChatService);
  private auth = inject(AuthService);

  messages = signal<ChatMessage[]>([]);
  conversationId = signal('');
  selectedCategory = signal('');
  isStreaming = signal(false);
  streamingContent = signal('');

  private shouldScroll = false;

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  async onSendMessage(text: string): Promise<void> {
    // Add user message to UI immediately
    const userMsg: ChatMessage = {
      id: 'temp-' + Date.now(),
      conversation_id: this.conversationId(),
      user_id: this.auth.user()?.id || '',
      role: 'user',
      content: text,
      source_documents: [],
      created_at: new Date().toISOString(),
    };
    this.messages.update(msgs => [...msgs, userMsg]);
    this.shouldScroll = true;

    // Start streaming
    this.isStreaming.set(true);
    this.streamingContent.set('');

    const request = {
      message: text,
      conversation_id: this.conversationId() || undefined,
      category_id: this.selectedCategory() || undefined,
    };

    let fullContent = '';
    let sources: SourceDocument[] = [];
    let messageId = '';

    try {
      for await (const chunk of this.chatService.streamMessageFetch(request)) {
        if (chunk.type === 'token') {
          fullContent += chunk.content;
          this.streamingContent.set(fullContent);
          this.shouldScroll = true;
        } else if (chunk.type === 'sources') {
          sources = chunk.sources;
        } else if (chunk.type === 'done') {
          this.conversationId.set(chunk.conversation_id);
          messageId = chunk.message_id;
        } else if (chunk.type === 'error') {
          fullContent = 'Error: ' + chunk.message;
          this.streamingContent.set(fullContent);
        }
      }
    } catch {
      fullContent = fullContent || 'Error al conectar con el servidor. Intente nuevamente.';
    }

    // Replace streaming with final message
    const assistantMsg: ChatMessage = {
      id: messageId || 'assistant-' + Date.now(),
      conversation_id: this.conversationId(),
      user_id: '',
      role: 'assistant',
      content: fullContent,
      source_documents: sources,
      created_at: new Date().toISOString(),
    };
    this.messages.update(msgs => [...msgs, assistantMsg]);
    this.isStreaming.set(false);
    this.streamingContent.set('');
    this.shouldScroll = true;
  }

  loadConversation(convId: string): void {
    this.conversationId.set(convId);
    this.chatService.getConversation(convId).subscribe({
      next: (res) => {
        this.messages.set(res.data.messages);
        this.shouldScroll = true;
      }
    });
  }

  startNewChat(): void {
    this.conversationId.set('');
    this.messages.set([]);
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer?.nativeElement;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    } catch {}
  }
}
