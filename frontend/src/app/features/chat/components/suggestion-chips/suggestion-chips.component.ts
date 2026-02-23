import { Component, EventEmitter, Output, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../services/chat.service';

const FALLBACK_QUESTIONS = [
  'Cuales son los requisitos de admision?',
  'Como solicito una beca?',
  'Cual es el calendario academico?',
  'Donde encuentro los silabos?',
  'Como realizo un tramite academico?',
  'Cuales son los servicios de bienestar?',
];

@Component({
  selector: 'app-suggestion-chips',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="text-center py-12">
      <span class="material-icons text-6xl text-primary-200 mb-4">school</span>
      <h2 class="text-xl font-semibold text-gray-700 mb-2">Bienvenido al Asistente UPAO</h2>
      <p class="text-gray-500 mb-8">Preguntame sobre la universidad. Aqui tienes algunas sugerencias:</p>
      <div class="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto">
        @if (isLoading()) {
          @for (i of skeletons; track i) {
            <div class="h-9 w-44 bg-gray-200 rounded-full animate-pulse"></div>
          }
        } @else {
          @for (question of questions(); track question) {
            <button (click)="selected.emit(question)"
                    class="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:bg-primary hover:text-white hover:border-primary transition-all shadow-sm">
              {{ question }}
            </button>
          }
        }
      </div>
    </div>
  `,
})
export class SuggestionChipsComponent implements OnInit {
  @Output() selected = new EventEmitter<string>();

  private chatService = inject(ChatService);
  questions = signal<string[]>([]);
  isLoading = signal(true);
  skeletons = [1, 2, 3, 4, 5, 6];

  ngOnInit(): void {
    this.chatService.getSuggestedQuestions().subscribe({
      next: res => {
        this.questions.set(res.data.questions);
        this.isLoading.set(false);
      },
      error: () => {
        this.questions.set(FALLBACK_QUESTIONS);
        this.isLoading.set(false);
      },
    });
  }
}
