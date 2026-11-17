import streamlit as st
import pandas as pd
from src.database.connection import test_connection
from src.services.atendimento_service import AtendimentoService
from src.services.estoque_service import EstoqueService
from src.services.financeiro_service import FinanceiroService

def render_home_view():
    st.title("🐾 PetFlow ERP — Painel Operacional")
    st.caption("Sistema Integrado de Gestão para Pet Shops e Clínicas Veterinárias • Padrão Acadêmico SI UFAPE 2026.2")

    # Status da conexão com Supabase
    conn_ok, conn_msg = test_connection()
    if not conn_ok:
        st.warning(f"⚠️ Atenção ao banco de dados: {conn_msg}. Verifique as credenciais no `.streamlit/secrets.toml`.")

    # 1. Indicadores Operacionais Rápidos
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        estetica_hoje = AtendimentoService.listar_atendimentos_estetica_dia()
        qtd_estetica = len(estetica_hoje)
    except Exception:
        estetica_hoje = []
        qtd_estetica = 0

    try:
        prods_criticos = EstoqueService.listar_posicao_estoque(apenas_criticos=True)
        qtd_criticos = len(prods_criticos)
    except Exception:
        prods_criticos = []
        qtd_criticos = 0

    try:
        resumo_fin = FinanceiroService.obter_resumo_caixa()
        saldo_caixa = resumo_fin["saldo_realizado"]
        pend_pagar = resumo_fin["a_pagar_pendente"]
    except Exception:
        saldo_caixa = 0.0
        pend_pagar = 0.0

    with col1:
        st.metric("🛁 Estética Hoje", f"{qtd_estetica} pets", help="Atendimentos de banho e tosa hoje")
    with col2:
        st.metric("⚠️ Estoque Crítico", f"{qtd_criticos} itens", delta=f"-{qtd_criticos}" if qtd_criticos > 0 else "0", delta_color="inverse")
    with col3:
        st.metric("💵 Saldo Realizado", f"R$ {saldo_caixa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col4:
        st.metric("⏳ A Pagar Pendente", f"R$ {pend_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta_color="inverse")

    st.markdown("---")

    # 2. Seções Operacionais em Duas Colunas
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📋 Fila do Dia — Banho & Tosa")
        if estetica_hoje:
            df_est = pd.DataFrame([
                {
                    "OS": item["numero_os"],
                    "Animal": f"{item['animal_nome']} ({item['codigo_prontuario']})",
                    "Tutor": item["tutor_nome"],
                    "Serviço": item["servico_nome"],
                    "Status": item["status"],
                    "Profissional": item["profissional_nome"],
                    "Alertas": ("⚠️ Pulgas " if item["tem_pulgas"] else "") + 
                               ("✂️ Nós " if item["tem_nos_pelagem"] else "") + 
                               ("🩹 Ferimento " if item["tem_ferimento_previo"] else "") or "✅ Normal"
                }
                for item in estetica_hoje
            ])
            st.dataframe(df_est, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum atendimento de estética em andamento para hoje. Realize novos check-ins no menu **Operacional**.")

        st.subheader("🩺 Consultas Médicas Recentes (Padrão HVU)")
        try:
            consultas = AtendimentoService.listar_consultas_recentes(limit=5)
            if consultas:
                df_cons = pd.DataFrame([
                    {
                        "Prontuário": item["codigo_prontuario"],
                        "Animal": item["animal_nome"],
                        "Tutor": item["tutor_nome"],
                        "Veterinário": f"Dr(a). {item['veterinario_nome']} ({item['crmv']})",
                        "Queixa Principal": item["queixa_principal"][:40] + "..." if len(item["queixa_principal"]) > 40 else item["queixa_principal"],
                        "Valor": f"R$ {float(item['valor_consulta']):.2f}"
                    }
                    for item in consultas
                ])
                st.dataframe(df_cons, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma consulta médica recente registrada.")
        except Exception as e:
            st.error(f"Erro ao carregar consultas: {e}")

    with col_right:
        st.subheader("⚡ Alertas de Reposição de Estoque")
        if prods_criticos:
            for p in prods_criticos[:6]:
                st.error(f"**{p['nome']}** — Saldo: **{p['estoque_atual']} {p['unidade_medida']}** (Mínimo: {p['estoque_minimo']})")
        else:
            st.success("🎉 Todos os produtos estão com níveis de estoque acima do limite de segurança!")

        st.markdown("### 🚀 Ações Rápidas")
        st.markdown("""
        - 🛒 **Abrir PDV:** Registre vendas de balcão e fature ordens de serviço em 1 tela.
        - 🛁 **Novo Check-in:** Dê entrada em pets para banho/tosa com inspeção de segurança.
        - 🩺 **Nova Consulta:** Prontuário clínico estruturado com exame físico HVU.
        - 📦 **Registrar Compra:** Dê entrada em insumos de fornecedores com efeito dominó.
        """)

if __name__ == "__main__":
    render_home_view()
