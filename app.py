import streamlit as st

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="PetFlow ERP — Gestão Pet & Vet",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.auth.auth_manager import AuthManager
from src.views.home import render_home_view
from src.views.operacional_view import render_operacional_view
from src.views.pdv_view import render_pdv_view
from src.views.compras_view import render_compras_view
from src.views.estoque_view import render_estoque_view
from src.views.financeiro_view import render_financeiro_view
from src.views.cadastros_view import render_cadastros_view

def main():
    # Barra lateral: Identificação e Badge de Autenticação Google
    with st.sidebar:
        st.markdown("## 🐾 PetFlow ERP")
        st.caption("Gestão Integrada para Pet Shops e Clínicas Veterinárias")
        st.markdown("---")
        
        # Renderiza status da autenticação Google (compatível com Supabase & Streamlit Auth)
        user_info = AuthManager.render_user_badge()
        st.markdown("---")
        st.markdown(
            """
            <small style='color: gray;'>
            Disciplina: Sistemas de Informação 2026.2<br>
            Prof. Dr. Assuero Fonseca Ximenes<br>
            UFAPE — Ciência da Computação
            </small>
            """,
            unsafe_allow_html=True
        )

    # Navegação moderna do Streamlit (st.navigation)
    pages = {
        "Visão Geral": [
            st.Page(render_home_view, title="Painel Operacional", icon="🏠", default=True)
        ],
        "Operação & Vendas": [
            st.Page(render_operacional_view, title="Atendimento (Estética & Clínica)", icon="⚡"),
            st.Page(render_pdv_view, title="Frente de Caixa (Fast POS)", icon="🛒")
        ],
        "Suprimentos & Finanças": [
            st.Page(render_compras_view, title="Compras & Entrada NF", icon="📥"),
            st.Page(render_estoque_view, title="Estoque & Rastreabilidade", icon="📦"),
            st.Page(render_financeiro_view, title="Financeiro & Caixa", icon="💰")
        ],
        "Administração": [
            st.Page(render_cadastros_view, title="Cadastros Mestres", icon="🗂️")
        ]
    }

    nav = st.navigation(pages)
    nav.run()

if __name__ == "__main__":
    main()
