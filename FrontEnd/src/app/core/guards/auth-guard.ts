import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isLoggedIn()) {
    router.navigate(['/login']);
    return false;
  }

  // A ARMADILHA DO FRONTEND: Se precisa trocar a senha, chuta para a tela isolada
  if (authService.needsPasswordChange()) {
    router.navigate(['/trocar-senha']);
    return false;
  }

  return true;
};