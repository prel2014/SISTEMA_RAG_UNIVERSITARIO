import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { TokenService } from './token.service';
import { User, LoginRequest, RegisterRequest, AuthResponse, ApiResponse } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private currentUser = signal<User | null>(null);

  user = this.currentUser.asReadonly();
  isAuthenticated = computed(() => !!this.currentUser());
  isAdmin = computed(() => this.currentUser()?.role === 'admin');

  readonly ready: Promise<void>;

  constructor(
    private http: HttpClient,
    private router: Router,
    private tokenService: TokenService
  ) {
    this.ready = this.loadUser();
  }

  private async loadUser(): Promise<void> {
    if (this.tokenService.isLoggedIn()) {
      try {
        await firstValueFrom(this.getMe());
      } catch {
        this.tokenService.clearTokens();
        this.currentUser.set(null);
      }
    }
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap(response => {
        if (response.success) {
          this.tokenService.setTokens(response.data.access_token, response.data.refresh_token);
          this.currentUser.set(response.data.user);
        }
      })
    );
  }

  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/register`, data).pipe(
      tap(response => {
        if (response.success) {
          this.tokenService.setTokens(response.data.access_token, response.data.refresh_token);
          this.currentUser.set(response.data.user);
        }
      })
    );
  }

  getMe(): Observable<ApiResponse<{ user: User }>> {
    return this.http.get<ApiResponse<{ user: User }>>(`${this.apiUrl}/me`).pipe(
      tap(response => {
        if (response.success) {
          this.currentUser.set(response.data.user);
        }
      })
    );
  }

  refreshToken(): Observable<ApiResponse<{ access_token: string }>> {
    const refreshToken = this.tokenService.getRefreshToken();
    return this.http.post<ApiResponse<{ access_token: string }>>(
      `${this.apiUrl}/refresh`, {},
      { headers: { Authorization: `Bearer ${refreshToken}` } }
    ).pipe(
      tap(response => {
        if (response.success) {
          const currentRefresh = this.tokenService.getRefreshToken();
          this.tokenService.setTokens(response.data.access_token, currentRefresh || '');
        }
      })
    );
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/logout`, {}).subscribe({ error: () => {} });
    this.tokenService.clearTokens();
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }
}
