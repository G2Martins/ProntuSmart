import { AbstractControl, Validators } from '@angular/forms';
import { Indicador } from '../models/indicador.model';

export function indicadorTemLimites(indicador: Partial<Indicador> | null | undefined): boolean {
  return !!indicador && !indicador.sem_limitacao_valor;
}

export function descreverLimitesIndicador(indicador: Partial<Indicador> | null | undefined): string {
  if (!indicador) return '';
  if (indicador.sem_limitacao_valor) return 'Sem limitação de valor';

  const minimo = indicador.limite_minimo;
  const maximo = indicador.limite_maximo;
  const unidade = indicador.unidade_medida ? ` ${indicador.unidade_medida}` : '';

  if (minimo != null && maximo != null) {
    return `Intervalo permitido: ${minimo} a ${maximo}${unidade}`;
  }

  if (minimo != null) {
    return `Valor mínimo permitido: ${minimo}${unidade}`;
  }

  if (maximo != null) {
    return `Valor máximo permitido: ${maximo}${unidade}`;
  }

  return 'Sem limitação de valor';
}

export function aplicarValidadoresLimite(
  control: AbstractControl | null,
  indicador: Partial<Indicador> | null | undefined,
  required = false,
): void {
  if (!control) return;

  const validators = [];
  if (required) validators.push(Validators.required);

  if (indicadorTemLimites(indicador)) {
    if (indicador?.limite_minimo != null) validators.push(Validators.min(indicador.limite_minimo));
    if (indicador?.limite_maximo != null) validators.push(Validators.max(indicador.limite_maximo));
  }

  control.setValidators(validators);
  control.updateValueAndValidity({ emitEvent: false });
}

export function valorForaDoLimite(
  indicador: Partial<Indicador> | null | undefined,
  valor: number | string | null | undefined,
): boolean {
  if (!indicadorTemLimites(indicador) || valor === '' || valor == null) return false;

  const numero = Number(valor);
  if (Number.isNaN(numero)) return false;

  return (
    (indicador?.limite_minimo != null && numero < indicador.limite_minimo) ||
    (indicador?.limite_maximo != null && numero > indicador.limite_maximo)
  );
}
