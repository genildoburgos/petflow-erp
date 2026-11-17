import streamlit as st
import pandas as pd
from src.services.venda_service import VendaService, EstoqueInsuficienteError
from src.services.cadastro_service import CadastroService
from src.services.atendimento_service import AtendimentoService

def render_pdv_view():
    st.title("🛒 Frente de Caixa — Fast POS")
    st.caption("Faturamento unificado em tela única: integre serviços de banho/tosa, consultas clínicas e produtos com baixa atômica de estoque e entrada no financeiro.")

    # Inicializa carrinho na sessão do Streamlit
    if "pdv_carrinho" not in st.session_state:
        st.session_state.pdv_carrinho = []
    if "pdv_servico_vinculado" not in st.session_state:
        st.session_state.pdv_servico_vinculado = None # {"tipo": "ESTETICA"|"CLINICA", "id": 1, "nome": "...", "valor": 65.0}

    # Carrega dados mestres
    try:
        colaboradores = CadastroService.listar_colaboradores()
        tutores = CadastroService.listar_tutores()
        produtos = CadastroService.listar_produtos(apenas_revenda=True)
        estetica_pendente = AtendimentoService.listar_estetica_pendente_pagamento()
        consultas_pendente = AtendimentoService.listar_consultas_pendente_pagamento()
    except Exception as e:
        colaboradores, tutores, produtos, estetica_pendente, consultas_pendente = [], [], [], [], []
        st.error(f"Erro ao carregar dados do PDV: {e}")

    col_esquerda, col_direita = st.columns([3, 2])

    with col_esquerda:
        st.subheader("1. Identificação da Venda")
        c1, c2 = st.columns(2)
        with c1:
            dict_colabs = {f"{c['nome']} ({c['cargo']})": c["id"] for c in colaboradores}
            caixa_sel = st.selectbox("Operador de Caixa *", options=list(dict_colabs.keys())) if dict_colabs else None
        with c2:
            dict_tutores = {"Cliente Balcão (Não identificado)": None}
            dict_tutores.update({f"{t['nome']} ({t['telefone']})": t["id"] for t in tutores})
            tutor_sel = st.selectbox("Cliente / Tutor", options=list(dict_tutores.keys()))

        st.markdown("---")
        st.subheader("2. Faturar Serviço Pronto (1 Clique)")
        
        col_srv1, col_srv2 = st.columns(2)
        with col_srv1:
            st.markdown("**🛁 Banho & Tosa Prontos:**")
            if estetica_pendente:
                dict_est = {f"{e['numero_os']} - {e['animal_nome']} ({e['servico_nome']}) | R$ {float(e['valor_servico']):.2f}": e for e in estetica_pendente}
                est_sel = st.selectbox("Selecione OS para faturar:", ["Nenhum"] + list(dict_est.keys()), key="sel_est_pdv")
                if est_sel != "Nenhum" and st.button("➕ Adicionar OS ao Carrinho"):
                    item_est = dict_est[est_sel]
                    st.session_state.pdv_servico_vinculado = {
                        "tipo": "ESTETICA",
                        "id": item_est["id"],
                        "nome": f"OS {item_est['numero_os']} - {item_est['servico_nome']} ({item_est['animal_nome']})",
                        "valor": float(item_est["valor_servico"])
                    }
                    st.success("OS adicionada ao carrinho!")
                    st.rerun()
            else:
                st.caption("Nenhum banho/tosa aguardando pagamento.")

        with col_srv2:
            st.markdown("**🩺 Consultas Clínicas Finalizadas:**")
            if consultas_pendente:
                dict_cons = {f"{c['numero_consulta']} - {c['animal_nome']} (Dr(a) {c['veterinario_nome']}) | R$ {float(c['valor_consulta']):.2f}": c for c in consultas_pendente}
                cons_sel = st.selectbox("Selecione Consulta para faturar:", ["Nenhum"] + list(dict_cons.keys()), key="sel_cons_pdv")
                if cons_sel != "Nenhum" and st.button("➕ Adicionar Consulta ao Carrinho"):
                    item_cons = dict_cons[cons_sel]
                    st.session_state.pdv_servico_vinculado = {
                        "tipo": "CLINICA",
                        "id": item_cons["id"],
                        "nome": f"Consulta {item_cons['numero_consulta']} - {item_cons['animal_nome']}",
                        "valor": float(item_cons["valor_consulta"])
                    }
                    st.success("Consulta adicionada ao carrinho!")
                    st.rerun()
            else:
                st.caption("Nenhuma consulta aguardando pagamento.")

        st.markdown("---")
        st.subheader("3. Adicionar Produtos de Varejo")
        dict_prods = {f"{p['nome']} (Estoque: {p['estoque_atual']} {p['unidade_medida']}) - R$ {float(p['preco_venda']):.2f}": p for p in produtos}
        
        col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
        with col_p1:
            prod_sel = st.selectbox("Buscar Produto:", options=list(dict_prods.keys())) if dict_prods else None
        with col_p2:
            qtd_item = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0)
        with col_p3:
            st.write("")
            st.write("")
            if st.button("➕ Adicionar", use_container_width=True):
                if prod_sel:
                    prod_info = dict_prods[prod_sel]
                    # Adiciona ao carrinho
                    st.session_state.pdv_carrinho.append({
                        "produto_id": prod_info["id"],
                        "nome": prod_info["nome"],
                        "quantidade": float(qtd_item),
                        "preco_unitario": float(prod_info["preco_venda"]),
                        "subtotal": float(qtd_item) * float(prod_info["preco_venda"])
                    })
                    st.rerun()

    with col_direita:
        st.subheader("🛒 Resumo do Carrinho")
        
        # Exibe serviço vinculado se houver
        subtotal_servico = 0.0
        if st.session_state.pdv_servico_vinculado:
            srv = st.session_state.pdv_servico_vinculado
            subtotal_servico = srv["valor"]
            with st.container(border=True):
                st.markdown(f"**🏷️ Serviço:** {srv['nome']}")
                st.markdown(f"**Valor:** R$ {srv['valor']:.2f}")
                if st.button("❌ Remover Serviço"):
                    st.session_state.pdv_servico_vinculado = None
                    st.rerun()

        # Exibe itens de produtos
        subtotal_produtos = 0.0
        if st.session_state.pdv_carrinho:
            df_itens = []
            for idx, item in enumerate(st.session_state.pdv_carrinho):
                subtotal_produtos += item["subtotal"]
                df_itens.append({
                    "Item": item["nome"],
                    "Qtd": item["quantidade"],
                    "Preço Un": f"R$ {item['preco_unitario']:.2f}",
                    "Total": f"R$ {item['subtotal']:.2f}"
                })
            st.dataframe(pd.DataFrame(df_itens), use_container_width=True, hide_index=True)
            if st.button("🗑️ Limpar Produtos"):
                st.session_state.pdv_carrinho = []
                st.rerun()
        else:
            if not st.session_state.pdv_servico_vinculado:
                st.info("O carrinho está vazio.")

        subtotal_geral = subtotal_produtos + subtotal_servico
        st.markdown("---")

        col_desc, col_pgto = st.columns(2)
        with col_desc:
            desconto = st.number_input("Desconto (R$)", min_value=0.0, max_value=float(subtotal_geral) if subtotal_geral > 0 else 0.0, value=0.0, step=1.0)
        with col_pgto:
            forma_pgto = st.selectbox("Forma de Pagamento *", ["PIX", "CARTAO_CREDITO", "CARTAO_DEBITO", "DINHEIRO", "FIADO_PARCELADO"])

        valor_total = max(0.0, subtotal_geral - desconto)

        st.metric(
            label="VALOR TOTAL A PAGAR",
            value=f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            help=f"Subtotal: R$ {subtotal_geral:.2f} - Desconto: R$ {desconto:.2f}"
        )

        obs_venda = st.text_input("Observações da Venda (Opcional)")

        st.write("")
        btn_finalizar = st.button("✅ FINALIZAR VENDA (EFEITO DOMINÓ)", type="primary", use_container_width=True)
        if btn_finalizar:
            if not caixa_sel:
                st.error("Selecione o Operador de Caixa.")
            elif subtotal_geral <= 0:
                st.error("Adicione ao menos um produto ou serviço ao carrinho.")
            else:
                try:
                    atendimento_id = st.session_state.pdv_servico_vinculado["id"] if st.session_state.pdv_servico_vinculado and st.session_state.pdv_servico_vinculado["tipo"] == "ESTETICA" else None
                    consulta_id = st.session_state.pdv_servico_vinculado["id"] if st.session_state.pdv_servico_vinculado and st.session_state.pdv_servico_vinculado["tipo"] == "CLINICA" else None

                    res_venda = VendaService.finalizar_venda(
                        colaborador_caixa_id=dict_colabs[caixa_sel],
                        forma_pagamento=forma_pgto,
                        itens_produtos=st.session_state.pdv_carrinho,
                        tutor_id=dict_tutores[tutor_sel],
                        atendimento_estetica_id=atendimento_id,
                        consulta_id=consulta_id,
                        desconto=desconto,
                        observacoes=obs_venda
                    )

                    st.balloons()
                    st.success(f"🎉 Venda **{res_venda['numero_venda']}** concluída com sucesso!")
                    st.info("Efeito dominó executado: Estoque baixado com trava atômica, OS finalizada e Receita lançada no Financeiro!")
                    
                    # Limpa carrinho
                    st.session_state.pdv_carrinho = []
                    st.session_state.pdv_servico_vinculado = None
                except EstoqueInsuficienteError as ee:
                    st.error(f"❌ Falha de Estoque: {ee}")
                except Exception as e:
                    st.error(f"❌ Erro ao finalizar venda: {e}")

    # Histórico de vendas do dia
    st.markdown("---")
    st.subheader("📋 Vendas Concluídas Recentemente")
    try:
        vendas = VendaService.listar_vendas_recentes(limit=10)
        if vendas:
            df_v = pd.DataFrame([
                {
                    "Número Venda": v["numero_venda"],
                    "Data/Hora": pd.to_datetime(v["data_venda"]).strftime("%d/%m/%Y %H:%M"),
                    "Cliente/Tutor": v["tutor_nome"],
                    "Operador Caixa": v["operador_caixa"],
                    "Pagamento": v["forma_pagamento"],
                    "Valor Total": f"R$ {float(v['valor_total']):.2f}",
                    "Status": v["status"]
                }
                for v in vendas
            ])
            st.dataframe(df_v, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar histórico de vendas: {e}")

if __name__ == "__main__":
    render_pdv_view()
