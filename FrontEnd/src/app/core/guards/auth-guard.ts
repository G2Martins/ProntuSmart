import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Se o usuário tem o token no localStorage, deixa passar
  if (authService.isLoggedIn()) {
    return true;
  }

  // Se não tem, chuta ele de volta para a tela de login
  router.navigate(['/login']);
  return false;
};