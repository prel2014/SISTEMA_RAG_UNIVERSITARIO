import {
  Component, EventEmitter, HostListener, Input, OnDestroy, OnInit, Output, inject, signal
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, EMPTY } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, takeUntil } from 'rxjs/operators';
import { ChatService, AutocompleteSuggestion } from '../../services/chat.service';

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="border-t bg-white p-4">
      <div class="max-w-4xl mx-auto">
        <form (ngSubmit)="onSend()" class="flex items-end space-x-3">
          <div class="flex-1 relative chat-input-wrapper">
            @if (showDropdown()) {
              <ul class="absolute bottom-full left-0 right-0 mb-1 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden z-50"
                  role="listbox">
                @for (item of suggestions(); track item.text; let i = $index) {
                  <li
                    [class.bg-primary]="activeIndex() === i"
                    [class.text-white]="activeIndex() === i"
                    class="flex items-center justify-between px-4 py-2 cursor-pointer hover:bg-gray-50 text-sm"
                    (mousedown)="$event.preventDefault(); onSelectSuggestion(item.text)"
                    role="option"
                    [attr.aria-selected]="activeIndex() === i"
                  >
                    <span class="truncate">{{ item.text }}</span>
                    <span class="ml-2 flex-shrink-0 text-xs px-1.5 py-0.5 rounded"
                          [class]="item.source === 'history' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
                      {{ item.source === 'history' ? 'historial' : 'documento' }}
                    </span>
                  </li>
                }
              </ul>
            }
            <textarea
              [ngModel]="message"
              (ngModelChange)="onInputChange($event)"
              name="message"
              [disabled]="disabled"
              (keydown)="onKeyDown($event)"
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
export class ChatInputComponent implements OnInit, OnDestroy {
  @Input() disabled = false;
  @Output() messageSent = new EventEmitter<string>();

  message = '';
  suggestions = signal<AutocompleteSuggestion[]>([]);
  showDropdown = signal(false);
  activeIndex = signal(-1);

  private searchInput$ = new Subject<string>();
  private destroy$ = new Subject<void>();
  private chatService = inject(ChatService);

  ngOnInit(): void {
    this.searchInput$.pipe(
      debounceTime(350),
      distinctUntilChanged(),
      switchMap(query => {
        if (query.length < 3) {
          this.suggestions.set([]);
          this.showDropdown.set(false);
          return EMPTY;
        }
        return this.chatService.getAutocompleteSuggestions(query);
      }),
      takeUntil(this.destroy$)
    ).subscribe({
      next: res => {
        this.suggestions.set(res.data.suggestions);
        this.showDropdown.set(res.data.suggestions.length > 0);
        this.activeIndex.set(-1);
      },
      error: () => {
        this.suggestions.set([]);
        this.showDropdown.set(false);
      },
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onInputChange(value: string): void {
    this.message = value;
    this.searchInput$.next(value.trim());
  }

  onSelectSuggestion(text: string): void {
    this.message = text;
    this.showDropdown.set(false);
    this.suggestions.set([]);
    this.activeIndex.set(-1);
  }

  onKeyDown(event: KeyboardEvent): void {
    if (this.showDropdown()) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        this.activeIndex.set(Math.min(this.activeIndex() + 1, this.suggestions().length - 1));
        return;
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        this.activeIndex.set(Math.max(this.activeIndex() - 1, -1));
        return;
      }
      if (event.key === 'Escape') {
        this.showDropdown.set(false);
        this.activeIndex.set(-1);
        return;
      }
      if (event.key === 'Enter' && this.activeIndex() >= 0) {
        event.preventDefault();
        this.onSelectSuggestion(this.suggestions()[this.activeIndex()].text);
        return;
      }
    }

    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onSend();
    }
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.chat-input-wrapper')) {
      this.showDropdown.set(false);
    }
  }

  onSend(): void {
    const text = this.message.trim();
    if (text && !this.disabled) {
      this.messageSent.emit(text);
      this.message = '';
      this.showDropdown.set(false);
      this.suggestions.set([]);
    }
  }
}
