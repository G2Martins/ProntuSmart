import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common'; 
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive], // <-- ADICIONADO AQUI
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './layout.html'
})
export class LayoutComponent {
  private authService = inject(AuthService);
  userProfile = this.authService.getUserProfile();

  logout() {
    this.authService.logout();
    window.location.href = '/login'; 
  }
}