import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminSidebarComponent } from '../../components/admin-sidebar/admin-sidebar.component';
import { ChatPageComponent } from '../../../chat/pages/chat-page/chat-page.component';

@Component({
  selector: 'app-test-chat',
  standalone: true,
  imports: [CommonModule, AdminSidebarComponent, ChatPageComponent],
  template: `
    <div class="flex">
      <app-admin-sidebar />
      <div class="flex-1">
        <div class="bg-primary-50 border-b border-primary-100 px-6 py-2">
          <p class="text-sm text-primary font-medium">
            <span class="material-icons text-sm align-middle mr-1">science</span>
            Modo de prueba - Las conversaciones se guardan como chat normal
          </p>
        </div>
        <app-chat-page />
      </div>
    </div>
  `,
})
export class TestChatComponent {}
