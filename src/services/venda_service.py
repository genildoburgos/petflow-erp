import datetime
from sqlalchemy import text
from src.database.connection import get_engine

class EstoqueInsuficienteError(Exception):
    pass

class VendaService:
    @staticmethod
    def listar_vendas_recentes(limit: int = 20):
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    v.id, v.numero_venda, v.data_venda, v.valor_total, v.forma_pagamento, v.status,
                    COALESCE(t.nome, 'Cliente Balcão') AS tutor_nome,
                    c.nome AS operador_caixa
                FROM vendas v
                LEFT JOIN tutores t ON v.tutor_id = t.id
                JOIN colaboradores c ON v.colaborador_caixa_id = c.id
                ORDER BY v.data_venda DESC
                LIMIT :limit
            """)
            return conn.execute(query, {"limit": limit}).mappings().all()

    @staticmethod
    def finalizar_venda(
        colaborador_caixa_id: int,
        forma_pagamento: str,
        itens_produtos: list[dict], # [{"produto_id": 1, "quantidade": 2, "preco_unitario": 50.0}]
        tutor_id: int | None = None,
        atendimento_estetica_id: int | None = None,
        consulta_id: int | None = None,
        desconto: float = 0.0,
        observacoes: str = ""
    ) -> dict:
        """
        Orquestra o EFEITO DOMINÓ da Venda dentro de uma transação atômica:
        1. Insere cabeçalho da Venda
        2. Insere Itens da Venda
        3. Atualiza Saldo de Estoque e gera Log em movimentacoes_estoque
        4. Atualiza status de OS de banho/consulta caso vinculada
        5. Lança Receita no módulo Financeiro
        """
        engine = get_engine()
        
        with engine.begin() as conn:
            # 1. Calcula totais de produtos
            subtotal_produtos = sum(item["quantidade"] * item["preco_unitario"] for item in itens_produtos)
            
            # Adiciona valor de serviço se houver
            valor_servico = 0.0
            if atendimento_estetica_id:
                servico_row = conn.execute(
                    text("SELECT valor_servico FROM atendimentos_estetica WHERE id = :id"),
                    {"id": atendimento_estetica_id}
                ).mappings().first()
                if servico_row:
                    valor_servico += float(servico_row["valor_servico"])
                    
            if consulta_id:
                consulta_row = conn.execute(
                    text("SELECT valor_consulta FROM consultas_veterinarias WHERE id = :id"),
                    {"id": consulta_id}
                ).mappings().first()
                if consulta_row:
                    valor_servico += float(consulta_row["valor_consulta"])

            subtotal_geral = subtotal_produtos + valor_servico
            valor_total = max(0.0, subtotal_geral - desconto)

            # Gera número único da venda
            agora = datetime.datetime.now()
            numero_venda = f"VD-{agora.strftime('%Y%m%d%H%M%S')}"

            # 2. Insere Venda
            insert_venda = text("""
                INSERT INTO vendas (
                    numero_venda, tutor_id, atendimento_estetica_id, consulta_id,
                    colaborador_caixa_id, subtotal, desconto, valor_total,
                    forma_pagamento, status, observacoes
                ) VALUES (
                    :numero_venda, :tutor_id, :atendimento_id, :consulta_id,
                    :colaborador_id, :subtotal, :desconto, :valor_total,
                    :forma_pagamento, 'FINALIZADA', :observacoes
                ) RETURNING id
            """)
            venda_id = conn.execute(insert_venda, {
                "numero_venda": numero_venda,
                "tutor_id": tutor_id,
                "atendimento_id": atendimento_estetica_id,
                "consulta_id": consulta_id,
                "colaborador_id": colaborador_caixa_id,
                "subtotal": subtotal_geral,
                "desconto": desconto,
                "valor_total": valor_total,
                "forma_pagamento": forma_pagamento,
                "observacoes": observacoes
            }).scalar()

            # 3. Processa cada produto vendido (Efeito Dominó no Estoque)
            for item in itens_produtos:
                prod_id = item["produto_id"]
                qtd = item["quantidade"]
                preco_un = item["preco_unitario"]

                # Verifica estoque atual com trava de linha (SELECT FOR UPDATE)
                prod = conn.execute(
                    text("SELECT nome, estoque_atual FROM produtos WHERE id = :id FOR UPDATE"),
                    {"id": prod_id}
                ).mappings().first()

                if not prod:
                    raise ValueError(f"Produto ID {prod_id} não encontrado.")

                estoque_ant = float(prod["estoque_atual"])
                if estoque_ant < qtd:
                    raise EstoqueInsuficienteError(
                        f"Estoque insuficiente para '{prod['nome']}'. Disponível: {estoque_ant}, Solicitado: {qtd}"
                    )

                estoque_pos = estoque_ant - qtd

                # Insere item_venda
                conn.execute(
                    text("""
                        INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario)
                        VALUES (:venda_id, :produto_id, :quantidade, :preco_unitario)
                    """),
                    {"venda_id": venda_id, "produto_id": prod_id, "quantidade": qtd, "preco_unitario": preco_un}
                )

                # Atualiza saldo do produto
                conn.execute(
                    text("UPDATE produtos SET estoque_atual = :novo_saldo, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                    {"novo_saldo": estoque_pos, "id": prod_id}
                )

                # Registra log imutável de movimentação
                conn.execute(
                    text("""
                        INSERT INTO movimentacoes_estoque (
                            produto_id, tipo_movimento, quantidade,
                            estoque_anterior, estoque_posterior,
                            origem_modulo, origem_id, justificativa
                        ) VALUES (
                            :produto_id, 'SAIDA_VENDA_PDV', :quantidade,
                            :estoque_anterior, :estoque_posterior,
                            'VENDAS', :origem_id, :justificativa
                        )
                    """),
                    {
                        "produto_id": prod_id,
                        "quantidade": -qtd,
                        "estoque_anterior": estoque_ant,
                        "estoque_posterior": estoque_pos,
                        "origem_id": venda_id,
                        "justificativa": f"Venda PDV {numero_venda}"
                    }
                )

            # 4. Atualiza status de OS operacional se vinculada
            if atendimento_estetica_id:
                conn.execute(
                    text("UPDATE atendimentos_estetica SET status = 'FINALIZADO_ENTREGUE', data_hora_conclusao = CURRENT_TIMESTAMP WHERE id = :id"),
                    {"id": atendimento_estetica_id}
                )

            if consulta_id:
                conn.execute(
                    text("UPDATE consultas_veterinarias SET status = 'FINALIZADA' WHERE id = :id"),
                    {"id": consulta_id}
                )

            # 5. Efeito Dominó no Financeiro (Entrada de Receita Imediata)
            conn.execute(
                text("""
                    INSERT INTO financeiro_lancamentos (
                        tipo, categoria_financeira, descricao, valor,
                        status, forma_pagamento, origem_modulo, origem_id,
                        data_competencia, data_vencimento, data_pagamento
                    ) VALUES (
                        'RECEITA', 'VENDA_BALCAO', :descricao, :valor,
                        'PAGO', :forma_pagamento, 'VENDAS', :origem_id,
                        CURRENT_DATE, CURRENT_DATE, CURRENT_DATE
                    )
                """),
                {
                    "descricao": f"Recebimento {numero_venda}",
                    "valor": valor_total,
                    "forma_pagamento": forma_pagamento,
                    "origem_id": venda_id
                }
            )

            return {
                "venda_id": venda_id,
                "numero_venda": numero_venda,
                "valor_total": valor_total,
                "status": "FINALIZADA"
            }
