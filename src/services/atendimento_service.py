import datetime
from decimal import Decimal
from sqlalchemy import text
from src.database.connection import get_engine
from src.utils.money import to_decimal, round_money

class AtendimentoService:
    @staticmethod
    def listar_atendimentos_estetica_dia():
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    ae.id, ae.numero_os, ae.status, ae.valor_servico, ae.valor_comissao,
                    ae.data_hora_entrada, ae.tem_pulgas, ae.tem_nos_pelagem, ae.tem_ferimento_previo,
                    a.nome AS animal_nome, a.codigo_prontuario,
                    t.nome AS tutor_nome, t.telefone AS tutor_whatsapp,
                    s.nome AS servico_nome,
                    c.nome AS profissional_nome
                FROM atendimentos_estetica ae
                JOIN animais a ON ae.animal_id = a.id
                JOIN tutores t ON a.tutor_id = t.id
                JOIN servicos s ON ae.servico_id = s.id
                JOIN colaboradores c ON ae.colaborador_id = c.id
                WHERE ae.data_hora_entrada::DATE = CURRENT_DATE
                ORDER BY ae.data_hora_entrada DESC
            """)
            return conn.execute(query).mappings().all()

    @staticmethod
    def criar_atendimento_estetica(
        animal_id: int,
        servico_id: int,
        colaborador_id: int,
        tem_pulgas: bool = False,
        tem_nos_pelagem: bool = False,
        tem_ferimento_previo: bool = False,
        foto_checkin_url: str | None = None,
        observacoes_manejo: str = ""
    ) -> dict:
        engine = get_engine()
        with engine.begin() as conn:
            # Puxa valor base e comissão
            servico = conn.execute(
                text("SELECT preco_base, comissao_padrao_pct FROM servicos WHERE id = :id"),
                {"id": servico_id}
            ).mappings().first()

            colaborador = conn.execute(
                text("SELECT percentual_comissao FROM colaboradores WHERE id = :id"),
                {"id": colaborador_id}
            ).mappings().first()

            valor_servico = float(round_money(servico["preco_base"]))
            pct_comissao = float(to_decimal(servico["comissao_padrao_pct"] or colaborador["percentual_comissao"] or 0.0))

            agora = datetime.datetime.now()
            numero_os = f"OS-{agora.strftime('%Y%m%d%H%M%S')}"

            insert_query = text("""
                INSERT INTO atendimentos_estetica (
                    numero_os, animal_id, servico_id, colaborador_id, status,
                    valor_servico, percentual_comissao, tem_pulgas,
                    tem_nos_pelagem, tem_ferimento_previo, foto_checkin_url,
                    observacoes_manejo
                ) VALUES (
                    :numero_os, :animal_id, :servico_id, :colaborador_id, 'RECEBIDO_CHECKIN',
                    :valor_servico, :pct_comissao, :tem_pulgas,
                    :tem_nos, :tem_ferimento, :foto, :obs
                ) RETURNING id
            """)
            os_id = conn.execute(insert_query, {
                "numero_os": numero_os,
                "animal_id": animal_id,
                "servico_id": servico_id,
                "colaborador_id": colaborador_id,
                "valor_servico": valor_servico,
                "pct_comissao": pct_comissao,
                "tem_pulgas": tem_pulgas,
                "tem_nos": tem_nos_pelagem,
                "tem_ferimento": tem_ferimento_previo,
                "foto": foto_checkin_url,
                "obs": observacoes_manejo
            }).scalar()

            return {"id": os_id, "numero_os": numero_os, "valor_servico": valor_servico}

    @staticmethod
    def atualizar_status_estetica(
        atendimento_id: int, 
        novo_status: str, 
        insumos_utilizados: list[dict] | None = None # [{"produto_id": 1, "quantidade": 0.1}]
    ):
        """
        Atualiza o status operacional do banho/tosa.
        Se concluído, gera baixa de insumos consumidos e provisão de comissão no financeiro.
        """
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE atendimentos_estetica SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                {"status": novo_status, "id": atendimento_id}
            )

            # Baixa de insumos se fornecido
            if insumos_utilizados:
                for insumo in insumos_utilizados:
                    prod_id = insumo["produto_id"]
                    qtd = float(insumo["quantidade"])

                    prod = conn.execute(
                        text("SELECT estoque_atual FROM produtos WHERE id = :id FOR UPDATE"),
                        {"id": prod_id}
                    ).mappings().first()

                    if prod:
                        est_ant = float(prod["estoque_atual"])
                        est_pos = max(0.0, est_ant - qtd)

                        conn.execute(
                            text("INSERT INTO insumos_estetica (atendimento_estetica_id, produto_id, quantidade_utilizada) VALUES (:atend_id, :prod_id, :qtd)"),
                            {"atend_id": atendimento_id, "prod_id": prod_id, "qtd": qtd}
                        )

                        conn.execute(
                            text("UPDATE produtos SET estoque_atual = :saldo WHERE id = :id"),
                            {"saldo": est_pos, "id": prod_id}
                        )

                        conn.execute(
                            text("""
                                INSERT INTO movimentacoes_estoque (
                                    produto_id, tipo_movimento, quantidade,
                                    estoque_anterior, estoque_posterior,
                                    origem_modulo, origem_id, justificativa
                                ) VALUES (
                                    :prod_id, 'SAIDA_CONSUMO_ESTETICA', :qtd,
                                    :ant, :pos, 'ESTETICA', :atend_id, 'Consumo de Insumo no Atendimento'
                                )
                            """),
                            {"prod_id": prod_id, "qtd": -qtd, "ant": est_ant, "pos": est_pos, "atend_id": atendimento_id}
                        )

            # Se finalizado, provisiona comissão no Financeiro
            if novo_status in ('PRONTO_AVISAR', 'FINALIZADO_ENTREGUE'):
                atend = conn.execute(
                    text("SELECT numero_os, valor_comissao, colaborador_id FROM atendimentos_estetica WHERE id = :id"),
                    {"id": atendimento_id}
                ).mappings().first()

                if atend and float(atend["valor_comissao"]) > 0:
                    # Verifica se já não foi lançado
                    ja_existe = conn.execute(
                        text("SELECT id FROM financeiro_lancamentos WHERE origem_modulo = 'ESTETICA' AND origem_id = :id"),
                        {"id": atendimento_id}
                    ).scalar()

                    if not ja_existe:
                        conn.execute(
                            text("""
                                INSERT INTO financeiro_lancamentos (
                                    tipo, categoria_financeira, descricao, valor,
                                    status, origem_modulo, origem_id,
                                    data_competencia, data_vencimento
                                ) VALUES (
                                    'DESPESA', 'COMISSAO_COLABORADOR', :desc, :val,
                                    'PENDENTE', 'ESTETICA', :id,
                                    CURRENT_DATE, CURRENT_DATE + INTERVAL '7 days'
                                )
                            """),
                            {
                                "desc": f"Comissão {atend['numero_os']}",
                                "val": float(atend["valor_comissao"]),
                                "id": atendimento_id
                            }
                        )

    @staticmethod
    def registrar_consulta_clinica(
        animal_id: int,
        veterinario_id: int,
        peso_atual: float,
        queixa_principal: str,
        tipo_consulta: str = "PRIMEIRA_VEZ",
        alteracoes_clinicas: str = "",
        suspeitas_clinicas: str = "",
        alimentacao: str = "",
        temperatura: float | None = None,
        frequencia_cardiaca: int | None = None,
        frequencia_respiratoria: int | None = None,
        tpc: int | None = None,
        parecer_diagnostico: str = "",
        prescricoes_lista: list[dict] | None = None, # [{"medicamento_id": 1, "dose": "...", "frequencia": "...", "periodo_dias": 7}]
        insumos_consumidos: list[dict] | None = None, # [{"produto_id": 3, "quantidade": 1.0}] (ex: vacina)
        valor_consulta: float = 150.00
    ) -> dict:
        """
        Registra a consulta médica veterinária completa (padrão HVU) e orquestra
        o efeito dominó no estoque (vacinas/remédios) e financeiro (comissão).
        """
        engine = get_engine()
        with engine.begin() as conn:
            vet = conn.execute(
                text("SELECT percentual_comissao FROM colaboradores WHERE id = :id"),
                {"id": veterinario_id}
            ).mappings().first()

            pct_comissao = float(vet["percentual_comissao"] if vet else 0.0)

            agora = datetime.datetime.now()
            num_cons = f"CONS-{agora.strftime('%Y%m%d%H%M%S')}"

            # 1. Insere Consulta
            insert_cons = text("""
                INSERT INTO consultas_veterinarias (
                    numero_consulta, animal_id, veterinario_id, peso_atual,
                    tipo_consulta, queixa_principal, alteracoes_clinicas_diversas,
                    suspeitas_clinicas, alimentacao, temperatura_celsius,
                    frequencia_cardiaca_bpm, frequencia_respiratoria_mpm, tpc_segundos,
                    parecer_diagnostico, valor_consulta, percentual_comissao, status
                ) VALUES (
                    :num, :animal_id, :vet_id, :peso,
                    :tipo, :queixa, :alteracoes,
                    :suspeitas, :alim, :temp,
                    :fc, :fr, :tpc,
                    :parecer, :valor, :comissao_pct, 'FINALIZADA'
                ) RETURNING id
            """)
            consulta_id = conn.execute(insert_cons, {
                "num": num_cons,
                "animal_id": animal_id,
                "vet_id": veterinario_id,
                "peso": peso_atual,
                "tipo": tipo_consulta,
                "queixa": queixa_principal,
                "alteracoes": alteracoes_clinicas,
                "suspeitas": suspeitas_clinicas,
                "alim": alimentacao,
                "temp": temperatura,
                "fc": frequencia_cardiaca,
                "fr": frequencia_respiratoria,
                "tpc": tpc,
                "parecer": parecer_diagnostico,
                "valor": valor_consulta,
                "comissao_pct": pct_comissao
            }).scalar()

            # 2. Prescrições
            if prescricoes_lista:
                for p in prescricoes_lista:
                    conn.execute(
                        text("""
                            INSERT INTO prescricoes (
                                consulta_id, medicamento_id, dose, frequencia, periodo_dias, observacoes_administracao
                            ) VALUES (:cid, :mid, :dose, :freq, :dias, :obs)
                        """),
                        {
                            "cid": consulta_id,
                            "mid": p["medicamento_id"],
                            "dose": p["dose"],
                            "freq": p["frequencia"],
                            "dias": p["periodo_dias"],
                            "obs": p.get("observacoes", "")
                        }
                    )

            # 3. Baixa de Vacinas / Insumos no Estoque
            if insumos_consumidos:
                for ins in insumos_consumidos:
                    prod_id = ins["produto_id"]
                    qtd = float(ins["quantidade"])

                    prod = conn.execute(
                        text("SELECT estoque_atual FROM produtos WHERE id = :id FOR UPDATE"),
                        {"id": prod_id}
                    ).mappings().first()

                    if prod:
                        est_ant = float(prod["estoque_atual"])
                        est_pos = max(0.0, est_ant - qtd)

                        conn.execute(
                            text("INSERT INTO insumos_consulta (consulta_id, produto_id, quantidade_utilizada) VALUES (:cid, :pid, :qtd)"),
                            {"cid": consulta_id, "pid": prod_id, "qtd": qtd}
                        )
                        conn.execute(
                            text("UPDATE produtos SET estoque_atual = :saldo WHERE id = :id"),
                            {"saldo": est_pos, "id": prod_id}
                        )
                        conn.execute(
                            text("""
                                INSERT INTO movimentacoes_estoque (
                                    produto_id, tipo_movimento, quantidade,
                                    estoque_anterior, estoque_posterior,
                                    origem_modulo, origem_id, justificativa
                                ) VALUES (
                                    :pid, 'SAIDA_CONSUMO_CLINICA', :qtd,
                                    :ant, :pos, 'CLINICA', :cid, 'Insumo/Vacina aplicada em consulta'
                                )
                            """),
                            {"pid": prod_id, "qtd": -qtd, "ant": est_ant, "pos": est_pos, "cid": consulta_id}
                        )

            # 4. Provisão de comissão do veterinário no Financeiro com precisão Decimal
            valor_cons_dec = round_money(valor_consulta)
            pct_com_dec = to_decimal(pct_comissao)
            valor_comissao = round_money(valor_cons_dec * (pct_com_dec / Decimal("100.0")))
            if valor_comissao > 0:
                conn.execute(
                    text("""
                        INSERT INTO financeiro_lancamentos (
                            tipo, categoria_financeira, descricao, valor,
                            status, origem_modulo, origem_id,
                            data_competencia, data_vencimento
                        ) VALUES (
                            'DESPESA', 'COMISSAO_COLABORADOR', :desc, :val,
                            'PENDENTE', 'CLINICA', :cid,
                            CURRENT_DATE, CURRENT_DATE + INTERVAL '15 days'
                        )
                    """),
                    {
                        "desc": f"Comissão Veterinária {num_cons}",
                        "val": float(valor_comissao),
                        "cid": consulta_id
                    }
                )

            return {"consulta_id": consulta_id, "numero_consulta": num_cons, "valor": valor_consulta}

    @staticmethod
    def listar_consultas_recentes(limit: int = 20):
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    cv.id, cv.numero_consulta, cv.data_consulta, cv.tipo_consulta,
                    cv.queixa_principal, cv.valor_consulta, cv.status,
                    a.nome AS animal_nome, a.codigo_prontuario,
                    t.nome AS tutor_nome, t.telefone AS tutor_whatsapp,
                    c.nome AS veterinario_nome, c.crmv
                FROM consultas_veterinarias cv
                JOIN animais a ON cv.animal_id = a.id
                JOIN tutores t ON a.tutor_id = t.id
                JOIN colaboradores c ON cv.veterinario_id = c.id
                ORDER BY cv.data_consulta DESC
                LIMIT :limit
            """)
            return conn.execute(query, {"limit": limit}).mappings().all()

    @staticmethod
    def listar_estetica_pendente_pagamento():
        """Retorna ordens de estética concluídas que ainda não foram faturadas em vendas."""
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    ae.id, ae.numero_os, ae.valor_servico, ae.status,
                    a.nome AS animal_nome, a.tutor_id,
                    t.nome AS tutor_nome,
                    s.nome AS servico_nome
                FROM atendimentos_estetica ae
                JOIN animais a ON ae.animal_id = a.id
                JOIN tutores t ON a.tutor_id = t.id
                JOIN servicos s ON ae.servico_id = s.id
                LEFT JOIN vendas v ON v.atendimento_estetica_id = ae.id
                WHERE ae.status IN ('PRONTO_AVISAR', 'FINALIZADO_ENTREGUE')
                  AND v.id IS NULL
                ORDER BY ae.data_hora_entrada DESC
            """)
            return conn.execute(query).mappings().all()

    @staticmethod
    def listar_consultas_pendente_pagamento():
        """Retorna consultas médicas finalizadas que ainda não foram faturadas em vendas."""
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    cv.id, cv.numero_consulta, cv.valor_consulta,
                    a.nome AS animal_nome, a.tutor_id,
                    t.nome AS tutor_nome,
                    c.nome AS veterinario_nome
                FROM consultas_veterinarias cv
                JOIN animais a ON cv.animal_id = a.id
                JOIN tutores t ON a.tutor_id = t.id
                JOIN colaboradores c ON cv.veterinario_id = c.id
                LEFT JOIN vendas v ON v.consulta_id = cv.id
                WHERE cv.status = 'FINALIZADA'
                  AND v.id IS NULL
                ORDER BY cv.data_consulta DESC
            """)
            return conn.execute(query).mappings().all()

