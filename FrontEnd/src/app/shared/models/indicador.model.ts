export type DirecaoMelhora = 'maior_melhor' | 'menor_melhor';

export interface Indicador {
  _id: string;
  nome: string;
  descricao: string | null;
  unidade_medida: string;
  direcao_melhora: DirecaoMelhora;
  is_ativo: boolean;
  criado_em: string;
  atualizado_em: string;
}

export interface IndicadorCreate {
  nome: string;
  descricao?: string;
  unidade_medida: string;
  direcao_melhora: DirecaoMelhora;
}

export interface IndicadorUpdate {
  nome?: string;
  descricao?: string;
  unidade_medida?: string;
  direcao_melhora?: DirecaoMelhora;
}