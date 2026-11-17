import streamlit as st
import pandas as pd
from src.services.compra_service import CompraService
from src.services.cadastro_service import CadastroService

def render_compras_view():
    st.title("📦 Compras & Entrada de Mercadorias")
    st.caption("Entrada de notas fiscais de fornecedores com orquestração atômica: incremento de estoque, log de rastreabilidade e geração de contas a pagar no módulo financeiro.")

    # Inicializa carrinho de compras na sessão
    if "compra_itens" not in st.session_state:
        st.session_state.compra_itens = []

    try:
        fornecedores = CadastroService.listar_fornecedores()
        produtos = CadastroService.listar_produtos()
    except Exception as e:
        fornecedores, produtos = [], []
        st.error(f"Erro ao carregar dados: {e}")

    col_form, col_carrinho = st.columns([3, 2])

    with col_form:
        st.subheader("1. Dados da Nota Fiscal & Fornecedor")
        dict_forn = {f"{f['nome_fantasia']} ({f['cnpj']})": f["id"] for f in fornecedores}
        
        c1, c2 = st.columns(2)
        with c1:
            forn_sel = st.selectbox("Fornecedor *", options=list(dict_forn.keys())) if dict_forn else None
        with c2:
            num_nota = st.text_input("Número da Nota Fiscal / Pedido *", placeholder="NF-e 12345")

        st.markdown("---")
        st.subheader("2. Adicionar Itens da Compra")
        dict_prods = {f"{p['nome']} (Estoque atual: {p['estoque_atual']} {p['unidade_medida']})": p for p in produtos}

        cp1, cp2, cp3 = st.columns([3, 1, 1])
        with cp1:
            prod_sel = st.selectbox("Produto Comprado:", options=list(dict_prods.keys())) if dict_prods else None
        with cp2:
            qtd_compra = st.number_input("Quantidade", min_value=1.0, value=10.0, step=1.0)
        with cp3:
            custo_un = st.number_input("Custo Unit. (R$)", min_value=0.1, value=25.0, step=1.0)

        if st.button("➕ Adicionar Item à Lista de Compra", use_container_width=True):
            if prod_sel:
                p_info = dict_prods[prod_sel]
                st.session_state.compra_itens.append({
                    "produto_id": p_info["id"],
                    "nome": p_info["nome"],
                    "quantidade": float(qtd_compra),
                    "preco_unitario": float(custo_un),
                    "subtotal": float(qtd_compra) * float(custo_un)
                })
                st.rerun()

    with col_carrinho:
        st.subheader("📋 Itens da Nota")
        total_compra = 0.0

        if st.session_state.compra_itens:
            df_itens = []
            for item in st.session_state.compra_itens:
                total_compra += item["subtotal"]
                df_itens.append({
                    "Produto": item["nome"],
                    "Qtd": item["quantidade"],
                    "Custo Un": f"R$ {item['preco_unitario']:.2f}",
                    "Total": f"R$ {item['subtotal']:.2f}"
                })
            st.dataframe(pd.DataFrame(df_itens), use_container_width=True, hide_index=True)
            if st.button("🗑️ Limpar Itens"):
                st.session_state.compra_itens = []
                st.rerun()
        else:
            st.info("Nenhum item adicionado à nota ainda.")

        st.markdown("---")
        st.metric(
            label="VALOR TOTAL DA COMPRA",
            value=f"R$ {total_compra:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        vencimento_fin = st.date_input("Vencimento do Título a Pagar *")
        obs_compra = st.text_input("Observações da Compra (Opcional)")

        st.write("")
        btn_gravar = st.button("📥 REGISTRAR ENTRADA & EFETUAR DOMINÓ", type="primary", use_container_width=True)
        if btn_gravar:
            if not forn_sel or not num_nota:
                st.error("Fornecedor e Número da Nota são obrigatórios.")
            elif not st.session_state.compra_itens:
                st.error("Adicione ao menos um produto à lista de compra.")
            else:
                try:
                    res_compra = CompraService.registrar_compra(
                        fornecedor_id=dict_forn[forn_sel],
                        numero_nota=num_nota,
                        itens_produtos=st.session_state.compra_itens,
                        data_vencimento_financeiro=vencimento_fin.isoformat() if vencimento_fin else None,
                        observacoes=obs_compra
                    )
                    st.success(f"Entrada de mercadorias registrada com sucesso! ID da Compra: **{res_compra['compra_id']}**")
                    st.info(f"Efeito dominó aplicado: {len(st.session_state.compra_itens)} produtos tiveram saldo de estoque incrementado e um título de R$ {total_compra:.2f} foi provisionado no Financeiro.")
                    st.session_state.compra_itens = []
                except Exception as e:
                    st.error(f"Erro ao registrar compra: {e}")

    # Histórico de compras
    st.markdown("---")
    st.subheader("📜 Histórico de Compras Realizadas")
    try:
        compras = CompraService.listar_compras_recentes(limit=15)
        if compras:
            df_c = pd.DataFrame([
                {
                    "ID": c["id"],
                    "Nota Fiscal": c["numero_nota"],
                    "Fornecedor": c["fornecedor_nome"],
                    "Data": pd.to_datetime(c["data_compra"]).strftime("%d/%m/%Y"),
                    "Valor Total": f"R$ {float(c['valor_total']):.2f}",
                    "Status": c["status"]
                }
                for c in compras
            ])
            st.dataframe(df_c, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao listar compras: {e}")

if __name__ == "__main__":
    render_compras_view()
