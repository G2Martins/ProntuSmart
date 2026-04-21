export type DirecaoMelhora = 'maior_melhor' | 'menor_melhor';

export interface Indicador {
  _id: string;
  nome: string;
  descricao: string | null;
  unidade_medida: string;
  direcao_melhora: DirecaoMelhora;
  sem_limitacao_valor: boolean;
  limite_minimo: number | null;
  limite_maximo: number | null;
  is_ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export interface IndicadorCreate {
  nome: string;
  descricao?: string;
  unidade_medida: string;
  direcao_melhora: DirecaoMelhora;
  sem_limitacao_valor: boolean;
  limite_minimo?: number | null;
  limite_maximo?: number | null;
}

export interface IndicadorUpdate {
  nome?: string;
  descricao?: string;
  unidade_medida?: string;
  direcao_melhora?: DirecaoMelhora;
  sem_limitacao_valor?: boolean;
  limite_minimo?: number | null;
  limite_maximo?: number | null;
  is_ativo?: boolean;
}
