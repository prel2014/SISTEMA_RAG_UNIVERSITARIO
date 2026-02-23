import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { BehaviorSubject, catchError, filter, switchMap, take, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { TokenService } from '../services/token.service';

const SKIP_REFRESH_URLS = ['/auth/login', '/auth/register', '/auth/refresh', '/auth/logout'];

let isRefreshing = false;
let refreshSubject = new BehaviorSubject<string | null>(null);

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const tokenService = inject(TokenService);

  return next(req).pipe(
    catchError(error => {
      const shouldSkip = SKIP_REFRESH_URLS.some(url => req.url.includes(url));
      if (error.status !== 401 || shouldSkip) {
        return throwError(() => error);
      }

      if (isRefreshing) {
        // Wait for the in-flight refresh, then retry with the new token
        return refreshSubject.pipe(
          filter(token => token !== null),
          take(1),
          switchMap(token => {
            const clonedReq = req.clone({
              setHeaders: { Authorization: `Bearer ${token}` }
            });
            return next(clonedReq);
          })
        );
      }

      const tokenBeforeRefresh = tokenService.getAccessToken();
      isRefreshing = true;
      refreshSubject.next(null);

      return authService.refreshToken().pipe(
        switchMap(() => {
          const newToken = tokenService.getAccessToken();
          isRefreshing = false;
          refreshSubject.next(newToken);
          const clonedReq = req.clone({
            setHeaders: { Authorization: `Bearer ${newToken}` }
          });
          return next(clonedReq);
        }),
        catchError(refreshError => {
          isRefreshing = false;
          refreshSubject.next(null);
          // Solo cerrar sesion si no hubo un login nuevo durante el refresh
          const currentToken = tokenService.getAccessToken();
          if (!currentToken || currentToken === tokenBeforeRefresh) {
            authService.logout();
          }
          return throwError(() => refreshError);
        })
      );
    })
  );
};
