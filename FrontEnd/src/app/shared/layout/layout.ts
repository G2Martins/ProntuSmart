import { Component, inject, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { ThemeService } from '../../core/services/theme.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './layout.html'
})
export class LayoutComponent {
  private authService = inject(AuthService);
  protected themeService = inject(ThemeService);

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
      case 'Docente':       return 'from-brand-500 to-brand-700';
      default:              return 'from-brand-400 to-brand-600';
    }
  }

  get sidebarLogoSrc(): string {
    // Sidebar tem fundo escuro (brand-900), logo com texto em paleta funciona bem
    return this.themeService.isDark()
      ? 'assets/OriginalIco/LogoCompleta_FundoDarK_CorTextoBranco.png'
      : 'assets/LogoCompleta_FundoPaleta_CorTextoBranco.png';
  }

  toggleTheme(): void {
    this.themeService.toggle();
  }

  logout() {
    this.authService.logout();
    window.location.href = '/login';
  }
}
