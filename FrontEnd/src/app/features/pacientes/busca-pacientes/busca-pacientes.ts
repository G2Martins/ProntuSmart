import { Component, inject, OnInit, CUSTOM_ELEMENTS_SCHEMA, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged, switchMap, of } from 'rxjs';
import { PacienteService } from '../../../core/services/paciente.service';
import { AuthService } from '../../../core/services/auth.service';
import { ProntuarioService } from '../../../core/services/prontuario.service';
import { AdminService } from '../../../core/services/admin.service';
import { CidService } from '../../../core/services/cid.service';
import { HttpParams } from '@angular/common/http';

@Component({
  selector: 'app-busca-pacientes',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './busca-pacientes.html'
})
export class BuscaPacientesComponent implements OnInit {
  private pacienteService = inject(PacienteService);
  private authService = inject(AuthService);
  private prontuarioService = inject(ProntuarioService);
  private adminService = inject(AdminService);
  private cidService = inject(CidService);
  private cdr = inject(ChangeDetectorRef);
  private router = inject(Router);
  private fb = inject(FormBuilder);

  pacientes: any[] = [];
  termoBusca: string = '';
  isLoading = true;
  errorMessage = '';
  perfil: string | null = '';

  // Modal de Triagem
  mostrarModalTriagem = false;
  pacienteSelecionado: any = null;
  estagiariosDisponiveis: any[] = [];

  // CID com busca reativa
  termoBuscaCid: string = '';
  cidsFiltrados: any[] = [];
  cidSelecionado: any = null;
  buscandoCids = false;
  private cidSearch$ = new Subject<string>();

  areasDisponiveis = [
    "Saúde do Homem e da Mulher", "Geriatria", "Neurologia Adulto",
    "Neuropediatria", "Traumato-Ortopedia", "Cardiorrespiratória"
  ];

  triagemForm = this.fb.group({
    estagiario_id: ['', Validators.required],
    area_atendimento: ['', Validators.required],
    cid_id: ['', Validators.required]
  });

  ngOnInit() {
    this.perfil = this.authService.getUserProfile();
    this.carregarPacientes();

    if (this.perfil === 'Docente' || this.perfil === 'Administrador') {
      this.carregarEstagiarios();
    }

    // Busca reativa de CIDs com debounce de 300ms
    this.cidSearch$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(termo => {
        if (!termo || termo.length < 2) {
          return of([]);
        }
        this.buscandoCids = true;
        return this.cidService.buscar(termo, 50);
      })
    ).subscribe({
      next: (cids) => {
        this.cidsFiltrados = cids;
        this.buscandoCids = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.buscandoCids = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarEstagiarios() {
    this.adminService.listarEstagiarios().subscribe({
      next: (res) => {
        this.estagiariosDisponiveis = res;
        this.cdr.detectChanges();
      },
      error: (err) => console.error("Erro ao carregar estagiários:", err)
    });
  }

  onBuscaCidChange(termo: string) {
    this.termoBuscaCid = termo;
    this.cidSelecionado = null;
    this.triagemForm.patchValue({ cid_id: '' });
    this.cidSearch$.next(termo);
  }

  selecionarCidDaLista(cid: any) {
    this.cidSelecionado = cid;
    this.termoBuscaCid = `[${cid.codigo}] ${cid.descricao}`;
    this.cidsFiltrados = [];
    this.triagemForm.patchValue({ cid_id: cid._id });
    this.cdr.detectChanges();
  }

  carregarPacientes() {
    this.isLoading = true;
    this.pacienteService.listar().subscribe({
      next: (dados) => {
        this.pacientes = dados;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Erro ao carregar base de pacientes.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  get pacientesFiltrados() {
    if (!this.termoBusca) return this.pacientes;
    const termo = this.termoBusca.toLowerCase();
    return this.pacientes.filter(p =>
      p.nome_completo.toLowerCase().includes(termo) ||
      p.cpf.includes(termo) ||
      p.area_atendimento_atual.toLowerCase().includes(termo)
    );
  }

  abrirTriagem(paciente: any) {
    this.pacienteSelecionado = paciente;
    this.mostrarModalTriagem = true;
    this.triagemForm.reset({ area_atendimento: paciente.area_atendimento_atual });
    this.termoBuscaCid = '';
    this.cidsFiltrados = [];
    this.cidSelecionado = null;
  }

  fecharTriagem() {
    this.mostrarModalTriagem = false;
    this.pacienteSelecionado = null;
  }

  selecionarEstagiario(event: any) {
    const nomeSelecionado = event.target.value;
    const estagiario = this.estagiariosDisponiveis.find(e => e.nome_completo === nomeSelecionado);
    this.triagemForm.patchValue({ estagiario_id: estagiario?._id || '' });
  }

  salvarTriagem() {
  if (this.triagemForm.invalid) {
    this.triagemForm.markAllAsTouched();
    return;
  }

  const dadosProntuario = {
    paciente_id: this.pacienteSelecionado._id,
    estagiario_id: this.triagemForm.value.estagiario_id,
    area_atendimento: this.triagemForm.value.area_atendimento,
    cid_id: this.triagemForm.value.cid_id
  };

  this.prontuarioService.criarTriagem(dadosProntuario).subscribe({
    next: (prontuario) => {
      this.fecharTriagem();          // fecha primeiro
      this.cdr.detectChanges();      // força re-render
      alert(`✅ Triagem concluída! Prontuário ${prontuario.numero_prontuario} criado com sucesso.`);
    },
    error: (err) => {
      alert(err.error?.detail || 'Erro ao realizar a triagem. Verifique os dados.');
    }
  });
}

  abrirProntuario(paciente: any) {
    this.prontuarioService.buscarPorPaciente(paciente._id).subscribe({
      next: (prontuario) => {
        this.router.navigate(['/prontuarios/visao', prontuario._id]);
      },
      error: () => {
        alert(`O paciente ${paciente.nome_completo} ainda não passou por Triagem.`);
      }
    });
  }
}