import streamlit as st

# Configuração Base do Streamlit
st.set_page_config(
    page_title="PetFlow ERP — Gestão Pet & Vet Enterprise",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.auth.auth_manager import AuthManager
from src.utils.theme import apply_enterprise_theme
from src.views.login_view import render_login_view
from src.views.home import render_home_view
from src.views.operacional_view import render_operacional_view
from src.views.pdv_view import render_pdv_view
from src.views.compras_view import render_compras_view
from src.views.estoque_view import render_estoque_view
from src.views.financeiro_view import render_financeiro_view
from src.views.cadastros_view import render_cadastros_view

def main():
    # -------------------------------------------------------------------------
    # GATE DE AUTENTICAÇÃO OBRIGATÓRIO
    # Se o operador não estiver logado, exibe exclusivamente o Portal de Acesso
    # -------------------------------------------------------------------------
    if not st.session_state.get("authenticated", False):
        login_nav = st.navigation([st.Page(render_login_view, title="Acesso ao Sistema", icon="🔒")])
        login_nav.run()
        return

    # Injeta Design System Boutique SaaS
    apply_enterprise_theme()

    # Barra lateral: Identificação Corporativa e Badge do Operador Ativo
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
                <span style="font-size: 26px;">🐾</span>
                <span style="font-size: 20px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px;">PetFlow ERP</span>
            </div>
            <div style="font-size: 12px; color: #64748B; margin-bottom: 12px;">
                Gestão Integrada Clínica & Estética Pet
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # Badge do operador conectado com função e botão de logout
        AuthManager.render_user_badge()
        
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #94A3B8; font-size: 11px; line-height: 1.5;">
                <strong>PetFlow Enterprise</strong> • v2.4.0<br>
                SLA 99.9% • Conexão Segura SSL
            </div>
            """,
            unsafe_allow_html=True
        )

    # Navegação Corporativa Multi-Módulos
    pages = {
        "Visão Geral": [
            st.Page(render_home_view, title="Painel Executivo", icon="🏠", default=True)
        ],
        "Operação & Vendas": [
            st.Page(render_operacional_view, title="Atendimento Clínico & Estética", icon="⚡"),
            st.Page(render_pdv_view, title="Frente de Caixa (PDV)", icon="🛒")
        ],
        "Suprimentos & Finanças": [
            st.Page(render_compras_view, title="Compras & Entrada NF", icon="📥"),
            st.Page(render_estoque_view, title="Estoque & Rastreabilidade", icon="📦"),
            st.Page(render_financeiro_view, title="Financeiro & Caixa", icon="💰")
        ],
        "Administração": [
            st.Page(render_cadastros_view, title="Cadastros & Equipe", icon="🗂️")
        ]
    }

    nav = st.navigation(pages)
    nav.run()

if __name__ == "__main__":
    main()
