from sqlalchemy import text
from src.database.connection import get_engine

class EstoqueService:
    @staticmethod
    def listar_posicao_estoque(apenas_criticos: bool = False, categoria_id: int | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT 
                    p.id, p.nome, p.codigo_barras, p.tipo_produto, p.unidade_medida,
                    p.preco_custo, p.preco_venda, p.estoque_minimo, p.estoque_atual,
                    (p.estoque_atual * p.preco_custo) AS valor_total_custo,
                    (p.estoque_atual * p.preco_venda) AS valor_total_venda,
                    c.nome AS categoria_nome,
                    CASE 
                        WHEN p.estoque_atual <= 0 THEN 'ESGOTADO'
                        WHEN p.estoque_atual <= p.estoque_minimo THEN 'CRITICO'
                        ELSE 'NORMAL'
                    END AS status_nivel
                FROM produtos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE p.ativo = TRUE
            """
            params = {}
            if apenas_criticos:
                sql += " AND p.estoque_atual <= p.estoque_minimo"
            if categoria_id:
                sql += " AND p.categoria_id = :categoria_id"
                params["categoria_id"] = categoria_id
            sql += " ORDER BY status_nivel DESC, p.nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def listar_movimentacoes(produto_id: int | None = None, limit: int = 50):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT 
                    m.id, m.data_hora, m.tipo_movimento, m.quantidade,
                    m.estoque_anterior, m.estoque_posterior,
                    m.origem_modulo, m.origem_id, m.justificativa,
                    p.nome AS produto_nome, p.unidade_medida
                FROM movimentacoes_estoque m
                JOIN produtos p ON m.produto_id = p.id
            """
            params = {"limit": limit}
            if produto_id:
                sql += " WHERE m.produto_id = :produto_id"
                params["produto_id"] = produto_id
            sql += " ORDER BY m.data_hora DESC LIMIT :limit"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def registrar_ajuste_inventario(produto_id: int, nova_quantidade: float, justificativa: str) -> dict:
        """
        Ajuste de inventário físico com gravação de log auditável e imutável.
        """
        engine = get_engine()
        with engine.begin() as conn:
            # Trava a linha do produto
            res_prod = conn.execute(
                text("SELECT estoque_atual, nome FROM produtos WHERE id = :id FOR UPDATE"),
                {"id": produto_id}
            ).mappings().one()

            estoque_ant = float(res_prod["estoque_atual"])
            novo_est = float(nova_quantidade)
            diferenca = novo_est - estoque_ant

            conn.execute(
                text("UPDATE produtos SET estoque_atual = :novo, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                {"novo": novo_est, "id": produto_id}
            )

            res_mov = conn.execute(
                text("""
                    INSERT INTO movimentacoes_estoque (
                        produto_id, tipo_movimento, quantidade,
                        estoque_anterior, estoque_posterior,
                        origem_modulo, origem_id, justificativa
                    ) VALUES (
                        :produto_id, 'AJUSTE_INVENTARIO', :quantidade,
                        :ant, :post,
                        'INVENTARIO', :produto_id, :justificativa
                    ) RETURNING id
                """),
                {
                    "produto_id": produto_id,
                    "quantidade": diferenca,
                    "ant": estoque_ant,
                    "post": novo_est,
                    "justificativa": justificativa
                }
            )
            mov_id = res_mov.scalar_one()

            return {
                "produto_id": produto_id,
                "produto_nome": res_prod["nome"],
                "estoque_anterior": estoque_ant,
                "estoque_posterior": novo_est,
                "movimentacao_id": mov_id
            }
