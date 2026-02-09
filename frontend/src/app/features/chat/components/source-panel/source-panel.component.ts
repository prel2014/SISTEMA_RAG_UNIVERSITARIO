import { Component, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SourceDocument } from '../../../../core/models/chat.model';

@Component({
  selector: 'app-source-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="border border-gray-200 rounded-lg overflow-hidden">
      <button (click)="isExpanded.set(!isExpanded())"
              class="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-sm">
        <span class="flex items-center text-gray-600">
          <span class="material-icons text-sm mr-1">source</span>
          {{ sources.length }} fuente(s)
        </span>
        <span class="material-icons text-sm text-gray-400 transition-transform"
              [class.rotate-180]="isExpanded()">
          expand_more
        </span>
      </button>

      @if (isExpanded()) {
        <div class="divide-y divide-gray-100">
          @for (source of sources; track source.document_id + source.page) {
            <div class="px-3 py-2 text-xs">
              <div class="flex items-center justify-between">
                <span class="font-medium text-primary">{{ source.title }}</span>
                <span class="text-gray-400">Pag. {{ source.page }} | {{ (source.score * 100).toFixed(0) }}%</span>
              </div>
              <p class="text-gray-500 mt-1 line-clamp-2">{{ source.preview }}</p>
            </div>
          }
        </div>
      }
    </div>
  `,
})
export class SourcePanelComponent {
  @Input() sources: SourceDocument[] = [];
  isExpanded = signal(false);
}
