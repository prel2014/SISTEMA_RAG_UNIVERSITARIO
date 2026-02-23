import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { TokenService } from '../../../core/services/token.service';
import { ApiResponse, PaginatedResponse } from '../../../core/models/user.model';
import { ChatMessage, ChatRequest, Conversation } from '../../../core/models/chat.model';

export interface AutocompleteSuggestion {
  text: string;
  source: 'history' | 'document';
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private http = inject(HttpClient);
  private tokenService = inject(TokenService);
  private apiUrl = `${environment.apiUrl}/chat`;

  sendMessage(request: ChatRequest): Observable<ApiResponse<{ message: ChatMessage; conversation_id: string }>> {
    return this.http.post<ApiResponse<{ message: ChatMessage; conversation_id: string }>>(
      `${this.apiUrl}/message`, request
    );
  }

  streamMessage(request: ChatRequest): EventSource {
    // SSE requires manual EventSource since HttpClient doesn't support streaming natively
    // We'll use fetch with readable stream instead
    return null as any; // Handled by streamMessageFetch below
  }

  async *streamMessageFetch(request: ChatRequest): AsyncGenerator<any> {
    const token = this.tokenService.getAccessToken();
    const response = await fetch(`${this.apiUrl}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Error al conectar con el servidor');
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No se pudo leer la respuesta');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data;
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  }

  getConversations(page = 1): Observable<PaginatedResponse<Conversation>> {
    return this.http.get<PaginatedResponse<Conversation>>(
      `${this.apiUrl}/conversations`, { params: { page: page.toString() } }
    );
  }

  getConversation(conversationId: string): Observable<ApiResponse<{ messages: ChatMessage[] }>> {
    return this.http.get<ApiResponse<{ messages: ChatMessage[] }>>(
      `${this.apiUrl}/conversations/${conversationId}`
    );
  }

  deleteConversation(conversationId: string): Observable<ApiResponse<void>> {
    return this.http.delete<ApiResponse<void>>(
      `${this.apiUrl}/conversations/${conversationId}`
    );
  }

  sendFeedback(chatHistoryId: string, rating: 1 | -1, comment?: string): Observable<ApiResponse<void>> {
    return this.http.post<ApiResponse<void>>(
      `${this.apiUrl}/feedback`,
      { chat_history_id: chatHistoryId, rating, comment }
    );
  }

  getAutocompleteSuggestions(query: string): Observable<ApiResponse<{ suggestions: AutocompleteSuggestion[] }>> {
    return this.http.get<ApiResponse<{ suggestions: AutocompleteSuggestion[] }>>(
      `${this.apiUrl}/autocomplete`,
      { params: { q: query } }
    );
  }

  getSuggestedQuestions(): Observable<ApiResponse<{ questions: string[] }>> {
    return this.http.get<ApiResponse<{ questions: string[] }>>(
      `${this.apiUrl}/suggested-questions`
    );
  }
}
