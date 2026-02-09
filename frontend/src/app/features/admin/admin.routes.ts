import { Routes } from '@angular/router';

export const adminRoutes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
  },
  {
    path: 'documents',
    loadComponent: () => import('./pages/document-management/document-management.component').then(m => m.DocumentManagementComponent),
  },
  {
    path: 'categories',
    loadComponent: () => import('./pages/category-management/category-management.component').then(m => m.CategoryManagementComponent),
  },
  {
    path: 'users',
    loadComponent: () => import('./pages/user-management/user-management.component').then(m => m.UserManagementComponent),
  },
  {
    path: 'rag-config',
    loadComponent: () => import('./pages/rag-config/rag-config.component').then(m => m.RagConfigComponent),
  },
  {
    path: 'test-chat',
    loadComponent: () => import('./pages/test-chat/test-chat.component').then(m => m.TestChatComponent),
  },
];
