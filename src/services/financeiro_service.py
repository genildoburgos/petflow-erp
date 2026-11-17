import datetime
from sqlalchemy import text
from src.database.connection import get_engine

class FinanceiroService:
    @staticmethod
    def listar_lancamentos(
        tipo: str | None = None,
        status: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        limit: int = 100
    ):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT 
                    id, tipo, categoria_financeira, descricao, valor,
                    data_competencia, data_vencimento, data_pagamento,
                    status, forma_pagamento, origem_modulo, origem_id
                FROM financeiro_lancamentos
                WHERE 1=1
            """
            params = {"limit": limit}
            if tipo:
                sql += " AND tipo = :tipo"
                params["tipo"] = tipo
            if status:
                sql += " AND status = :status"
                params["status"] = status
            if data_inicio:
                sql += " AND data_competencia >= :data_inicio"
                params["data_inicio"] = data_inicio
            if data_fim:
                sql += " AND data_competencia <= :data_fim"
                params["data_fim"] = data_fim

            sql += " ORDER BY data_competencia DESC, id DESC LIMIT :limit"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def obter_resumo_caixa() -> dict:
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    COALESCE(SUM(CASE WHEN tipo = 'RECEITA' AND status = 'PAGO' THEN valor ELSE 0 END), 0) AS total_receitas_pagas,
                    COALESCE(SUM(CASE WHEN tipo = 'DESPESA' AND status = 'PAGO' THEN valor ELSE 0 END), 0) AS total_despesas_pagas,
                    COALESCE(SUM(CASE WHEN tipo = 'RECEITA' AND status = 'PENDENTE' THEN valor ELSE 0 END), 0) AS total_a_receber_pendente,
                    COALESCE(SUM(CASE WHEN tipo = 'DESPESA' AND status = 'PENDENTE' THEN valor ELSE 0 END), 0) AS total_a_pagar_pendente
                FROM financeiro_lancamentos
            """)
            row = conn.execute(query).mappings().one()
            saldo_realizado = float(row["total_receitas_pagas"]) - float(row["total_despesas_pagas"])
            return {
                "receitas_pagas": float(row["total_receitas_pagas"]),
                "despesas_pagas": float(row["total_despesas_pagas"]),
                "saldo_realizado": saldo_realizado,
                "a_receber_pendente": float(row["total_a_receber_pendente"]),
                "a_pagar_pendente": float(row["total_a_pagar_pendente"]),
                "saldo_projetado": saldo_realizado + float(row["total_a_receber_pendente"]) - float(row["total_a_pagar_pendente"])
            }

    @staticmethod
    def dar_baixa_lancamento(lancamento_id: int, forma_pagamento: str) -> None:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE financeiro_lancamentos
                    SET status = 'PAGO',
                        data_pagamento = CURRENT_DATE,
                        forma_pagamento = :forma,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """),
                {"id": lancamento_id, "forma": forma_pagamento}
            )

    @staticmethod
    def criar_lancamento_manual(
        tipo: str,
        categoria_financeira: str,
        descricao: str,
        valor: float,
        data_vencimento: str | datetime.date,
        status: str = "PAGO",
        forma_pagamento: str | None = "PIX"
    ) -> int:
        engine = get_engine()
        with engine.begin() as conn:
            data_pagto = datetime.date.today() if status == "PAGO" else None
            res = conn.execute(
                text("""
                    INSERT INTO financeiro_lancamentos (
                        tipo, categoria_financeira, descricao, valor,
                        data_competencia, data_vencimento, data_pagamento,
                        status, forma_pagamento, origem_modulo
                    ) VALUES (
                        :tipo, :categoria, :descricao, :valor,
                        CURRENT_DATE, :vencimento, :pagamento,
                        :status, :forma, 'MANUAL'
                    ) RETURNING id
                """),
                {
                    "tipo": tipo,
                    "categoria": categoria_financeira,
                    "descricao": descricao.strip(),
                    "valor": float(valor),
                    "vencimento": data_vencimento,
                    "pagamento": data_pagto,
                    "status": status,
                    "forma": forma_pagamento
                }
            )
            return res.scalar_one()
