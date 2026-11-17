from sqlalchemy import text
from src.database.connection import get_engine

class CompraService:
    @staticmethod
    def listar_compras_recentes(limit: int = 20):
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    c.id, c.numero_nota, c.data_compra, c.valor_total, c.status,
                    f.nome_fantasia AS fornecedor_nome
                FROM compras c
                JOIN fornecedores f ON c.fornecedor_id = f.id
                ORDER BY c.data_compra DESC
                LIMIT :limit
            """)
            return conn.execute(query, {"limit": limit}).mappings().all()

    @staticmethod
    def registrar_compra(
        fornecedor_id: int,
        numero_nota: str,
        itens_produtos: list[dict], # [{"produto_id": 1, "quantidade": 10, "preco_unitario": 20.0}]
        data_vencimento_financeiro: str | None = None,
        observacoes: str = ""
    ) -> dict:
        """
        Orquestra o EFEITO DOMINÓ da Compra:
        1. Insere Cabeçalho da Compra
        2. Insere Itens da Compra
        3. Atualiza Saldo de Estoque e Preço de Custo dos Produtos
        4. Registra Log imutável em movimentacoes_estoque
        5. Lança Título no Contas a Pagar do Módulo Financeiro
        """
        engine = get_engine()
        
        with engine.begin() as conn:
            valor_total = sum(item["quantidade"] * item["preco_unitario"] for item in itens_produtos)

            # 1. Insere Compra
            insert_compra = text("""
                INSERT INTO compras (fornecedor_id, numero_nota, valor_total, status, observacoes)
                VALUES (:fornecedor_id, :numero_nota, :valor_total, 'RECEBIDO', :observacoes)
                RETURNING id
            """)
            compra_id = conn.execute(insert_compra, {
                "fornecedor_id": fornecedor_id,
                "numero_nota": numero_nota,
                "valor_total": valor_total,
                "observacoes": observacoes
            }).scalar()

            # 2. Processa cada produto (Alimenta Estoque)
            for item in itens_produtos:
                prod_id = item["produto_id"]
                qtd = item["quantidade"]
                preco_custo = item["preco_unitario"]

                # Puxa saldo anterior
                prod = conn.execute(
                    text("SELECT estoque_atual FROM produtos WHERE id = :id FOR UPDATE"),
                    {"id": prod_id}
                ).mappings().first()

                if not prod:
                    raise ValueError(f"Produto ID {prod_id} não encontrado.")

                estoque_ant = float(prod["estoque_atual"])
                estoque_pos = estoque_ant + qtd

                # Insere item_compra
                conn.execute(
                    text("""
                        INSERT INTO itens_compra (compra_id, produto_id, quantidade, preco_unitario)
                        VALUES (:compra_id, :produto_id, :quantidade, :preco_unitario)
                    """),
                    {"compra_id": compra_id, "produto_id": prod_id, "quantidade": qtd, "preco_unitario": preco_custo}
                )

                # Atualiza estoque e preço de custo
                conn.execute(
                    text("""
                        UPDATE produtos 
                        SET estoque_atual = :novo_saldo, 
                            preco_custo = :preco_custo, 
                            updated_at = CURRENT_TIMESTAMP 
                        WHERE id = :id
                    """),
                    {"novo_saldo": estoque_pos, "preco_custo": preco_custo, "id": prod_id}
                )

                # Log de movimentação
                conn.execute(
                    text("""
                        INSERT INTO movimentacoes_estoque (
                            produto_id, tipo_movimento, quantidade,
                            estoque_anterior, estoque_posterior,
                            origem_modulo, origem_id, justificativa
                        ) VALUES (
                            :produto_id, 'ENTRADA_COMPRA', :quantidade,
                            :estoque_anterior, :estoque_posterior,
                            'COMPRAS', :origem_id, :justificativa
                        )
                    """),
                    {
                        "produto_id": prod_id,
                        "quantidade": qtd,
                        "estoque_anterior": estoque_ant,
                        "estoque_posterior": estoque_pos,
                        "origem_id": compra_id,
                        "justificativa": f"Entrada NF {numero_nota}"
                    }
                )

            # 3. Efeito Dominó no Financeiro (Contas a Pagar)
            conn.execute(
                text("""
                    INSERT INTO financeiro_lancamentos (
                        tipo, categoria_financeira, descricao, valor,
                        status, origem_modulo, origem_id,
                        data_competencia, data_vencimento
                    ) VALUES (
                        'DESPESA', 'COMPRA_FORNECEDOR', :descricao, :valor,
                        'PENDENTE', 'COMPRAS', :origem_id,
                        CURRENT_DATE, COALESCE(:vencimento, CURRENT_DATE + INTERVAL '30 days')
                    )
                """),
                {
                    "descricao": f"Fornecedor NF {numero_nota}",
                    "valor": valor_total,
                    "origem_id": compra_id,
                    "vencimento": data_vencimento_financeiro
                }
            )

            return {
                "compra_id": compra_id,
                "numero_nota": numero_nota,
                "valor_total": valor_total,
                "status": "RECEBIDO"
            }
