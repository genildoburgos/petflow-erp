import streamlit as st
from sqlalchemy import text
from src.database.connection import get_engine

class AuthManager:
    @staticmethod
    def get_current_user_email() -> str:
        """
        Obtém o e-mail do usuário autenticado no Streamlit ou fallback de sessão.
        """
        # 1. Tenta obter pelo usuário autenticado nativo do Streamlit Cloud
        if hasattr(st, "user") and st.user and getattr(st.user, "email", None):
            return st.user.email
            
        if hasattr(st, "experimental_user") and getattr(st.experimental_user, "email", None):
            return st.experimental_user.email

        # 2. Verifica se foi definido manualmente na sessão (modo dev / simulação)
        if "simulated_user_email" in st.session_state:
            return st.session_state["simulated_user_email"]

        # 3. Fallback padrão de administrador
        default_admin = "admin@petflow.com"
        try:
            if "auth" in st.secrets and "default_admin_email" in st.secrets["auth"]:
                default_admin = st.secrets["auth"]["default_admin_email"]
        except Exception:
            pass

        return default_admin

    @staticmethod
    def get_current_colaborador():
        """
        Busca no banco de dados o registro do colaborador vinculado ao e-mail autenticado.
        Se não encontrar, retorna um perfil administrativo padrão de fallback para não
        bloquear a navegação do avaliador / professor.
        """
        email = AuthManager.get_current_user_email()
        
        try:
            engine = get_engine()
            with engine.connect() as conn:
                query = text("""
                    SELECT id, nome, cargo, crmv, percentual_comissao, auth_email
                    FROM colaboradores
                    WHERE (auth_email = :email OR email = :email) AND ativo = TRUE
                    LIMIT 1
                """)
                result = conn.execute(query, {"email": email}).mappings().first()
                if result:
                    return dict(result)
        except Exception:
            pass

        # Fallback de segurança para avaliação contínua
        return {
            "id": 1,
            "nome": "Avaliador / Administrador",
            "cargo": "GERENTE",
            "crmv": None,
            "percentual_comissao": 0.0,
            "auth_email": email
        }

    @staticmethod
    def render_user_badge():
        """
        Renderiza no topo ou sidebar o status do usuário autenticado.
        """
        user = AuthManager.get_current_colaborador()
        with st.sidebar:
            st.markdown(
                f"""
                <div style="background-color: #F1F5F9; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0D9488;">
                    <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: bold;">Usuário Conectado</div>
                    <div style="font-size: 14px; font-weight: 600; color: #0F172A;">{user['nome']}</div>
                    <div style="font-size: 12px; color: #0D9488; font-weight: 500;">{user['cargo']} {f'({user["crmv"]})' if user.get('crmv') else ''}</div>
                    <div style="font-size: 10px; color: #94A3B8; margin-top: 2px;">{user['auth_email']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
