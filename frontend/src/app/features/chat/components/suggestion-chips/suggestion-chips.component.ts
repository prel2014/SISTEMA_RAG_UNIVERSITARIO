import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

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
        @for (suggestion of suggestions; track suggestion) {
          <button (click)="selected.emit(suggestion)"
                  class="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:bg-primary hover:text-white hover:border-primary transition-all shadow-sm">
            {{ suggestion }}
          </button>
        }
      </div>
    </div>
  `,
})
export class SuggestionChipsComponent {
  @Output() selected = new EventEmitter<string>();

  suggestions = [
    'Cuales son los requisitos de admision?',
    'Como solicito una beca?',
    'Cual es el calendario academico?',
    'Donde encuentro los silabos?',
    'Como realizo un tramite academico?',
    'Cuales son los servicios de bienestar?',
  ];
}
