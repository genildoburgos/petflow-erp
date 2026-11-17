import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import text
from src.database.connection import get_engine

load_dotenv()

class AuthManager:
    @staticmethod
    def get_google_sso_email() -> str | None:
        """
        Retorna o e-mail do usuário autenticado nativamente via Google SSO (Streamlit Cloud).
        """
        if hasattr(st, "user") and st.user and getattr(st.user, "email", None):
            return st.user.email
            
        if hasattr(st, "experimental_user") and getattr(st.experimental_user, "email", None):
            return st.experimental_user.email

        return None

    @staticmethod
    def get_current_user_email() -> str:
        """
        Obtém o e-mail do usuário ativo na sessão corporativa.
        """
        if "simulated_persona_email" in st.session_state and st.session_state["simulated_persona_email"]:
            return st.session_state["simulated_persona_email"]

        sso_email = AuthManager.get_google_sso_email()
        if sso_email:
            return sso_email

        return os.getenv("DEFAULT_ADMIN_EMAIL", "gnldburgos@gmail.com")

    @staticmethod
    def get_current_colaborador():
        """
        Carrega os dados e permissões do colaborador ativo na base de dados.
        """
        # Se já estiver em cache na sessão
        if "current_user" in st.session_state and st.session_state["current_user"]:
            return st.session_state["current_user"]

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
                    res_dict = dict(result)
                    st.session_state["current_user"] = res_dict
                    return res_dict
        except Exception:
            pass

        # Perfil executivo padrão
        default_user = {
            "id": 1,
            "nome": "Genildo Burgos",
            "cargo": "GERENTE",
            "crmv": None,
            "percentual_comissao": 0.0,
            "auth_email": email
        }
        st.session_state["current_user"] = default_user
        return default_user

    @staticmethod
    def render_user_badge():
        """
        Renderiza o card de operador conectado e botão de encerramento de sessão na barra lateral.
        """
        user = AuthManager.get_current_colaborador()
        
        cargo_label = {
            "VETERINARIO": f"Médica Veterinária ({user.get('crmv') or 'CRMV Ativo'})",
            "GERENTE": "Gestor Geral da Unidade",
            "TOSADOR": "Especialista em Estética Pet",
            "BANHISTA": "Operador de Banho & Higiene",
            "RECEPCIONISTA": "Atendimento & Frente de Loja"
        }.get(user.get("cargo", "GERENTE"), user.get("cargo", "Operador"))

        with st.sidebar:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 16px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 700; color: #0D9488; text-transform: uppercase; letter-spacing: 0.5px;">● Operador Ativo</span>
                        <span style="font-size: 11px; color: #64748B;">ID #{user.get('id', 1):03d}</span>
                    </div>
                    <div style="font-size: 14px; font-weight: 700; color: #0F172A; line-height: 1.3;">{user['nome']}</div>
                    <div style="font-size: 12px; color: #475569; margin-top: 2px;">{cargo_label}</div>
                    <div style="font-size: 11px; color: #94A3B8; margin-top: 4px; overflow: hidden; text-overflow: ellipsis;">{user.get('auth_email', '')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("🚪 Encerrar Sessão", use_container_width=True, key="btn_logout_sidebar"):
                st.session_state["authenticated"] = False
                st.session_state["current_user"] = None
                st.session_state["simulated_persona_email"] = None
                st.rerun()

        return user
