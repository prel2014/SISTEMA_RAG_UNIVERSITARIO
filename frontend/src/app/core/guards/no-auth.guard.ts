import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { TokenService } from '../services/token.service';

export const noAuthGuard: CanActivateFn = async () => {
  const authService = inject(AuthService);
  const tokenService = inject(TokenService);
  const router = inject(Router);

  await authService.ready;

  if (!tokenService.isLoggedIn()) {
    return true;
  }
  if (authService.isAdmin()) {
    return router.createUrlTree(['/admin']);
  }
  return router.createUrlTree(['/chat']);
};
