import streamlit as st
import pandas as pd
from src.services.financeiro_service import FinanceiroService

def render_financeiro_view():
    st.title("💰 Gestão Financeira & Fluxo de Caixa")
    st.caption("Visão integrada de receitas (vendas e serviços), despesas (compras e custos fixos) e conciliação de contas a pagar e receber.")

    # 1. Resumo do Caixa (KPIs Financeiros)
    try:
        resumo = FinanceiroService.obter_resumo_caixa()
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total Recebido", f"R$ {resumo['receitas_pagas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c2:
            st.metric("Total Pago", f"R$ {resumo['despesas_pagas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta_color="inverse")
        with c3:
            st.metric("Saldo em Caixa", f"R$ {resumo['saldo_realizado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c4:
            st.metric("A Receber (Pend.)", f"R$ {resumo['a_receber_pendente']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c5:
            st.metric("A Pagar (Pend.)", f"R$ {resumo['a_pagar_pendente']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta_color="inverse")
    except Exception as e:
        st.error(f"Erro ao carregar indicadores financeiros: {e}")

    st.markdown("---")

    tabs = st.tabs(["📑 Lançamentos & Conciliação", "➕ Novo Lançamento Manual (Despesa Fixa / Outros)"])

    # =========================================================================
    # TAB 1: LANÇAMENTOS & CONCILIAÇÃO
    # =========================================================================
    with tabs[0]:
        st.subheader("Extrato de Títulos Financeiros")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_tipo = st.selectbox("Filtrar por Tipo:", ["Todos", "RECEITA", "DESPESA"])
        with col_f2:
            filtro_status = st.selectbox("Filtrar por Status:", ["Todos", "PENDENTE", "PAGO"])

        try:
            tipo_param = None if filtro_tipo == "Todos" else filtro_tipo
            status_param = None if filtro_status == "Todos" else filtro_status

            lancamentos = FinanceiroService.listar_lancamentos(tipo=tipo_param, status=status_param, limit=100)

            if lancamentos:
                # Seção de Baixa Rápida de Título Pendente
                pendentes = [l for l in lancamentos if l["status"] == "PENDENTE"]
                if pendentes:
                    with st.expander("⚡ Baixa Rápida de Título Pendente (Efetivar Pagamento / Recebimento)", expanded=False):
                        dict_pend = {f"#{l['id']} - {l['tipo']} | {l['descricao']} (R$ {float(l['valor']):.2f})": l["id"] for l in pendentes}
                        col_b1, col_b2, col_b3 = st.columns([3, 2, 1])
                        with col_b1:
                            sel_baixa = st.selectbox("Selecione o Título:", options=list(dict_pend.keys()))
                        with col_b2:
                            forma_baixa = st.selectbox("Forma de Liquidação:", ["PIX", "DINHEIRO", "CARTAO_CREDITO", "CARTAO_DEBITO", "BOLETO"])
                        with col_b3:
                            st.write("")
                            st.write("")
                            if st.button("Confirmar Baixa", type="primary", use_container_width=True):
                                FinanceiroService.dar_baixa_lancamento(dict_pend[sel_baixa], forma_baixa)
                                st.success("Título baixado como PAGO com sucesso!")
                                st.rerun()

                df_lan = pd.DataFrame([
                    {
                        "ID": l["id"],
                        "Competência": pd.to_datetime(l["data_competencia"]).strftime("%d/%m/%Y"),
                        "Tipo": l["tipo"],
                        "Categoria": l["categoria_financeira"],
                        "Descrição": l["descricao"],
                        "Valor": f"R$ {float(l['valor']):.2f}",
                        "Vencimento": pd.to_datetime(l["data_vencimento"]).strftime("%d/%m/%Y") if l["data_vencimento"] else "-",
                        "Pagamento": pd.to_datetime(l["data_pagamento"]).strftime("%d/%m/%Y") if l["data_pagamento"] else "-",
                        "Forma": l["forma_pagamento"] or "-",
                        "Origem": l["origem_modulo"],
                        "Status": "🟢 PAGO" if l["status"] == "PAGO" else "🟡 PENDENTE"
                    }
                    for l in lancamentos
                ])
                st.dataframe(df_lan, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum lançamento financeiro encontrado.")
        except Exception as e:
            st.error(f"Erro ao consultar lançamentos: {e}")

    # =========================================================================
    # TAB 2: LANÇAMENTO MANUAL
    # =========================================================================
    with tabs[1]:
        st.subheader("Registro de Custos Operacionais Fixos / Outras Despesas")
        st.caption("Cadastre despesas como aluguel do imóvel, fatura de energia elétrica, internet ou custos avulsos.")

        with st.form("form_novo_lancamento_manual", clear_on_submit=True):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                tipo_man = st.selectbox("Tipo de Movimentação *", ["DESPESA", "RECEITA"])
                categoria_man = st.selectbox(
                    "Categoria Financeira *",
                    ["CUSTO_FIXO", "COMISSAO_COLABORADOR", "OUTROS", "VENDA_BALCAO"]
                )
                descricao_man = st.text_input("Descrição do Lançamento *", placeholder="Ex: Aluguel do ponto comercial - Ref. Novembro")
            with col_m2:
                valor_man = st.number_input("Valor (R$) *", min_value=0.01, value=1200.0, step=50.0)
                vencimento_man = st.date_input("Data de Vencimento *")
                status_man = st.selectbox("Situação Inicial *", ["PAGO", "PENDENTE"])
                forma_man = st.selectbox("Forma de Liquidação", ["PIX", "BOLETO", "DINHEIRO", "CARTAO_CREDITO", "CARTAO_DEBITO"])

            submitted_man = st.form_submit_button("Gravar Lançamento Financeiro", use_container_width=True)
            if submitted_man:
                if not descricao_man:
                    st.error("Informe a descrição do lançamento.")
                else:
                    try:
                        lid = FinanceiroService.criar_lancamento_manual(
                            tipo=tipo_man,
                            categoria_financeira=categoria_man,
                            descricao=descricao_man,
                            valor=valor_man,
                            data_vencimento=vencimento_man.isoformat(),
                            status=status_man,
                            forma_pagamento=forma_man if status_man == "PAGO" else None
                        )
                        st.success(f"Lançamento financeiro registrado com sucesso! ID: {lid}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar lançamento: {e}")

if __name__ == "__main__":
    render_financeiro_view()
