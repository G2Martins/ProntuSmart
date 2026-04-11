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
  userName    = this.authService.getUserName();

  get primeiroNome(): string {
    const nome = this.userName || this.userProfile || '';
    return nome.split(' ')[0];
  }

  getInitials(): string {
    const nome = this.userName || '';
    if (!nome) return (this.userProfile || '?')[0].toUpperCase();
    const parts = nome.trim().split(' ').filter((p: string) => p.length > 0);
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  get avatarGradient(): string {
    switch (this.userProfile) {
      case 'Administrador': return 'from-orange-500 to-red-500';
      case 'Docente':       return 'from-purple-500 to-indigo-600';
      default:              return 'from-blue-500 to-cyan-600';
    }
  }

  logout() {
    this.authService.logout();
    window.location.href = '/login';
  }
}