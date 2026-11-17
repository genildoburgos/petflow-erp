import streamlit as st
import pandas as pd
from src.services.estoque_service import EstoqueService
from src.services.cadastro_service import CadastroService

def render_estoque_view():
    st.title("📊 Gestão de Estoque & Rastreabilidade")
    st.caption("Controle físico-financeiro de insumos e produtos para revenda com log transacional imutável de movimentações.")

    tabs = st.tabs(["📦 Posição de Estoque", "🔄 Rastreabilidade de Movimentações", "⚖️ Ajuste de Inventário"])

    # =========================================================================
    # TAB 1: POSIÇÃO DE ESTOQUE
    # =========================================================================
    with tabs[0]:
        st.subheader("Saldo Atual & Níveis de Segurança")

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            try:
                categorias = CadastroService.listar_categorias()
                dict_cat = {"Todas as Categorias": None}
                dict_cat.update({c["nome"]: c["id"] for c in categorias})
                cat_sel = st.selectbox("Filtrar por Categoria:", options=list(dict_cat.keys()))
            except Exception:
                dict_cat, cat_sel = {}, None

        with col_f2:
            st.write("")
            apenas_criticos = st.checkbox("⚠️ Apenas Itens em Alerta / Críticos", value=False)

        try:
            itens_est = EstoqueService.listar_posicao_estoque(
                apenas_criticos=apenas_criticos,
                categoria_id=dict_cat.get(cat_sel)
            )

            if itens_est:
                total_custo = sum(float(i["valor_total_custo"] or 0) for i in itens_est)
                total_venda = sum(float(i["valor_total_venda"] or 0) for i in itens_est)
                itens_alerta = sum(1 for i in itens_est if i["status_nivel"] in ("CRITICO", "ESGOTADO"))

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Total de Itens Listados", len(itens_est))
                with m2:
                    st.metric("Itens Críticos/Esgotados", itens_alerta, delta=f"-{itens_alerta}" if itens_alerta > 0 else "0", delta_color="inverse")
                with m3:
                    st.metric("Patrimônio em Custo", f"R$ {total_custo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                with m4:
                    st.metric("Potencial em Venda", f"R$ {total_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

                st.markdown("---")

                df_pos = pd.DataFrame([
                    {
                        "ID": i["id"],
                        "Produto": i["nome"],
                        "Categoria": i["categoria_nome"],
                        "Tipo": i["tipo_produto"],
                        "Estoque Atual": f"{i['estoque_atual']} {i['unidade_medida']}",
                        "Estoque Mínimo": f"{i['estoque_minimo']} {i['unidade_medida']}",
                        "Preço Custo": f"R$ {float(i['preco_custo']):.2f}",
                        "Preço Venda": f"R$ {float(i['preco_venda']):.2f}",
                        "Total Custo": f"R$ {float(i['valor_total_custo'] or 0):.2f}",
                        "Nível": "🔴 ESGOTADO" if i["status_nivel"] == "ESGOTADO" else ("🟡 CRÍTICO" if i["status_nivel"] == "CRITICO" else "🟢 NORMAL")
                    }
                    for i in itens_est
                ])
                st.dataframe(df_pos, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum produto correspondente aos filtros selecionados.")
        except Exception as e:
            st.error(f"Erro ao consultar estoque: {e}")

    # =========================================================================
    # TAB 2: RASTREABILIDADE TEMPORAL (LOG IMUTÁVEL)
    # =========================================================================
    with tabs[1]:
        st.subheader("Log de Auditoria de Movimentações (Histórico Completo)")
        st.caption("Registro de toda entrada por compra, saída por venda PDV, consumo clínico de vacinas e consumo em banho/tosa.")

        try:
            movimentacoes = EstoqueService.listar_movimentacoes(limit=100)
            if movimentacoes:
                df_mov = pd.DataFrame([
                    {
                        "ID": m["id"],
                        "Data/Hora": pd.to_datetime(m["data_hora"]).strftime("%d/%m/%Y %H:%M:%S"),
                        "Produto": m["produto_nome"],
                        "Tipo Movimento": m["tipo_movimento"],
                        "Qtd": f"{float(m['quantidade']):+g} {m['unidade_medida']}",
                        "Saldo Anterior": f"{float(m['estoque_anterior']):g}",
                        "Novo Saldo": f"{float(m['estoque_posterior']):g}",
                        "Módulo": m["origem_modulo"],
                        "Justificativa": m["justificativa"] or "-"
                    }
                    for m in movimentacoes
                ])
                st.dataframe(df_mov, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma movimentação de estoque registrada até o momento.")
        except Exception as e:
            st.error(f"Erro ao consultar movimentações: {e}")

    # =========================================================================
    # TAB 3: AJUSTE DE INVENTÁRIO
    # =========================================================================
    with tabs[2]:
        st.subheader("Contagem Física & Ajuste de Inventário")
        st.caption("Utilize esta ferramenta para alinhar o saldo do sistema com a contagem física de prateleira.")

        with st.form("form_ajuste_estoque", clear_on_submit=True):
            try:
                produtos = CadastroService.listar_produtos()
                dict_p = {f"{p['nome']} (Saldo atual: {p['estoque_atual']} {p['unidade_medida']})": p for p in produtos}
            except Exception:
                dict_p = {}

            prod_ajuste_sel = st.selectbox("Selecione o Produto *", options=list(dict_p.keys())) if dict_p else None
            
            c_aj1, c_aj2 = st.columns(2)
            with c_aj1:
                nova_qtd = st.number_input("Nova Quantidade Contada *", min_value=0.0, value=10.0, step=1.0)
            with c_aj2:
                justificativa = st.text_input("Justificativa da Divergência *", placeholder="Ex: Quebra de frasco, avaria na entrega, contagem periódica...")

            submitted_ajuste = st.form_submit_button("Gravar Ajuste com Auditoria", use_container_width=True)
            if submitted_ajuste:
                if not prod_ajuste_sel or not justificativa:
                    st.error("Selecione o produto e informe uma justificativa válida.")
                else:
                    try:
                        p_selecionado = dict_p[prod_ajuste_sel]
                        res_aj = EstoqueService.registrar_ajuste_inventario(
                            produto_id=p_selecionado["id"],
                            nova_quantidade=nova_qtd,
                            justificativa=justificativa
                        )
                        st.success(f"Ajuste gravado com sucesso! Saldo de '{res_aj['produto_nome']}' alterado de {res_aj['estoque_anterior']} para **{res_aj['estoque_posterior']}**.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar ajuste: {e}")

if __name__ == "__main__":
    render_estoque_view()
