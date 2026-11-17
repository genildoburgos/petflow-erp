import streamlit as st
from sqlalchemy import text
from src.database.connection import get_engine

class AuthManager:
    @staticmethod
    def is_fallback_allowed() -> bool:
        """
        Indica se o modo de avaliação acadêmica (fallback) está permitido.
        Em ambiente de produção, configure st.secrets['auth']['allow_evaluator_fallback'] = false.
        """
        try:
            if "auth" in st.secrets and "allow_evaluator_fallback" in st.secrets["auth"]:
                return bool(st.secrets["auth"]["allow_evaluator_fallback"])
        except Exception:
            pass
        return True # Padrão True para apresentação acadêmica da disciplina

    @staticmethod
    def get_current_user_email() -> str:
        """
        Obtém o e-mail do usuário autenticado no Streamlit ou persona simulada.
        """
        # 1. Verifica se uma persona de teste foi selecionada para a apresentação
        if "simulated_persona_email" in st.session_state and st.session_state["simulated_persona_email"]:
            return st.session_state["simulated_persona_email"]

        # 2. Tenta obter pelo usuário autenticado nativo do Streamlit Cloud (Google Auth)
        if hasattr(st, "user") and st.user and getattr(st.user, "email", None):
            return st.user.email
            
        if hasattr(st, "experimental_user") and getattr(st.experimental_user, "email", None):
            return st.experimental_user.email

        # 3. Fallback padrão configurado no secrets
        try:
            if "auth" in st.secrets and "default_admin_email" in st.secrets["auth"]:
                return st.secrets["auth"]["default_admin_email"]
        except Exception:
            pass

        return "avaliador.ufape@gmail.com"

    @staticmethod
    def get_current_colaborador():
        """
        Busca no banco de dados o registro do colaborador vinculado ao e-mail autenticado.
        Se não encontrar e o modo de avaliação acadêmica estiver ativo, fornece o perfil de Avaliador.
        """
        email = AuthManager.get_current_user_email()
        is_fallback = False
        
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
                    res_dict["is_fallback"] = False
                    return res_dict
        except Exception:
            pass

        if not AuthManager.is_fallback_allowed():
            return None

        # Fallback explícito para ambiente acadêmico
        return {
            "id": 1,
            "nome": "Prof. Avaliador (UFAPE)",
            "cargo": "GERENTE",
            "crmv": None,
            "percentual_comissao": 0.0,
            "auth_email": email,
            "is_fallback": True
        }

    @staticmethod
    def render_user_badge():
        """
        Renderiza no topo ou sidebar o status do usuário autenticado e
        o seletor de personas para demonstração interativa na apresentação da 1ª VA.
        """
        user = AuthManager.get_current_colaborador()
        if not user:
            st.sidebar.error("Acesso não autorizado. E-mail não vinculado e fallback desabilitado.")
            st.stop()
            return None

        with st.sidebar:
            badge_color = "#E0F2FE" if not user["is_fallback"] else "#FEF3C7"
            border_color = "#0284C7" if not user["is_fallback"] else "#D97706"
            title_text = "Usuário Conectado (Google)" if not user["is_fallback"] else "Modo Avaliação Acadêmica (1ª VA)"

            st.markdown(
                f"""
                <div style="background-color: {badge_color}; padding: 10px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid {border_color};">
                    <div style="font-size: 10px; text-transform: uppercase; color: #475569; font-weight: bold;">{title_text}</div>
                    <div style="font-size: 13px; font-weight: 700; color: #0F172A;">{user['nome']}</div>
                    <div style="font-size: 11px; color: {border_color}; font-weight: 600;">{user['cargo']} {f'({user["crmv"]})' if user.get('crmv') else ''}</div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 2px;">{user['auth_email']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Seletor interativo de Persona para fins de demonstração acadêmica
            with st.expander("🎭 Simular Persona (Demonstração)", expanded=False):
                st.caption("Alterne de papel para testar regras de negócio, comissões e atendimentos:")
                personas = {
                    "Conta Google Atual": None,
                    "Dra. Camila (Veterinária - CRMV 4821)": "camila.vet@petflow.com",
                    "Lucas Ramos (Tosador Especialista)": "lucas.tosa@petflow.com",
                    "Mariana Duarte (Operadora de Caixa)": "mariana.caixa@petflow.com",
                    "Roberto Santos (Gerente Geral)": "roberto.gerente@petflow.com"
                }
                
                escolha = st.selectbox(
                    "Perfil Ativo:",
                    list(personas.keys()),
                    key="select_persona_simulator"
                )
                
                email_escolhido = personas[escolha]
                if st.session_state.get("simulated_persona_email") != email_escolhido:
                    st.session_state["simulated_persona_email"] = email_escolhido
                    st.rerun()

        return user
