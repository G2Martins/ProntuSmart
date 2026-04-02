import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './layout.html'
})
export class LayoutComponent {
  private authService = inject(AuthService);
  userProfile = this.authService.getUserProfile();

  logout() {
    this.authService.logout();
    window.location.href = '/login'; // Força o refresh da página e limpa estado
  }
}