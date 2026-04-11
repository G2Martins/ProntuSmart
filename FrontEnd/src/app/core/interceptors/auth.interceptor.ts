import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router      = inject(Router);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((err) => {
      // 401 em qualquer requisição = token expirado ou inválido
      if (err.status === 401) {
        const estaNoLogin = router.url.includes('/login');
        if (!estaNoLogin) {
          // Limpa token e redireciona para login sem loop
          authService.logout();
          router.navigate(['/login']);
        }
      }
      return throwError(() => err);
    })
  );
};