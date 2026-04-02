from bson import ObjectId
from fastapi import HTTPException
from src.core.database import get_database
from src.schemas.medicao import MedicaoCreate
from src.models.fato_medicao import FatoMedicao
from src.models.dim_status import StatusMeta
# Importaremos de helpers na próxima etapa
from src.utils.helpers import calcular_progresso

async def registrar_medicao(medicao_in: MedicaoCreate) -> dict:
    db = get_database()
    
    meta = await db.fato_meta_smart.find_one({"_id": ObjectId(medicao_in.meta_smart_id)})
    if not meta:
        raise HTTPException(status_code=404, detail="Meta SMART não encontrada.")
        
    indicador = await db.dim_indicador.find_one({"_id": meta["indicador_id"]})
    
    # Busca a última medição para definir o valor anterior. Se não houver, usa o valor_inicial da meta.
    ultima_medicao = await db.fato_medicao.find_one(
        {"meta_smart_id": ObjectId(medicao_in.meta_smart_id)},
        sort=[("data_medicao", -1)]
    )
    valor_anterior = ultima_medicao["valor_medido"] if ultima_medicao else meta["valor_inicial"]
    
    nova_medicao = FatoMedicao(
        **medicao_in.model_dump(),
        valor_anterior=valor_anterior
    )
    resultado = await db.fato_medicao.insert_one(nova_medicao.model_dump(by_alias=True, exclude_none=True))
    
    # Calcula o novo progresso
    novo_progresso = calcular_progresso(
        valor_inicial=meta["valor_inicial"],
        valor_alvo=meta["valor_alvo"],
        valor_atual=medicao_in.valor_medido,
        direcao=indicador["direcao_melhora"]
    )
    
    novo_status = StatusMeta.CONCLUIDA if novo_progresso >= 100.0 else StatusMeta.EM_ANDAMENTO
    
    # Atualiza a meta com o novo progresso e status
    await db.fato_meta_smart.update_one(
        {"_id": ObjectId(medicao_in.meta_smart_id)},
        {"$set": {"progresso_percentual": novo_progresso, "status": novo_status}}
    )
    
    return await db.fato_medicao.find_one({"_id": resultado.inserted_id})