import streamlit as st
from src.auth.auth_manager import AuthManager

def render_login_view():
    """
    Portal de Acesso e Autenticação Corporativa PetFlow Enterprise.
    Interface minimalista, moderna e sofisticada no padrão SaaS B2B.
    """
    # Injeta estilos específicos para a tela de autenticação centralizada
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* Oculta navegação e sidebar durante o login */
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }

        .login-wrapper {
            max-width: 460px;
            margin: 40px auto 20px auto;
            padding: 40px 36px;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .login-brand {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 8px;
        }
        .login-brand-icon {
            font-size: 32px;
        }
        .login-brand-name {
            font-size: 26px;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.5px;
        }
        .login-subtitle {
            font-size: 13px;
            color: #64748B;
            text-align: center;
            margin-bottom: 28px;
            line-height: 1.5;
        }
        .login-footer {
            margin-top: 32px;
            text-align: center;
            font-size: 11px;
            color: #94A3B8;
            line-height: 1.5;
        }
        .security-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #F1F5F9;
            color: #475569;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col_l, col_center, col_r = st.columns([1, 1.8, 1])

    with col_center:
        st.markdown(
            """
            <div class="login-wrapper">
                <div class="login-brand">
                    <span class="login-brand-icon">🐾</span>
                    <span class="login-brand-name">PetFlow ERP</span>
                </div>
                <div class="login-subtitle">
                    Sistema Integrado de Gestão Clínica Veterinária & Centro de Estética
                </div>
                <div style="text-align: center;">
                    <div class="security-badge">
                        🔒 Acesso Corporativo Seguro • SSL 256-bit
                    </div>
                </div>
            """,
            unsafe_allow_html=True
        )

        tab_estacao, tab_google = st.tabs(["Estação de Trabalho", "Google SSO"])

        with tab_estacao:
            st.caption("Selecione sua credencial homologada para acessar o ambiente:")
            
            perfis = {
                "Dra. Juliana Aguiar — Diretoria Clínica & Cirurgia": {
                    "email": "juliana.vet@gmail.com",
                    "nome": "Dra. Juliana Aguiar",
                    "cargo": "VETERINARIO",
                    "crmv": "CRMV-PE 12345"
                },
                "Genildo Burgos — Gestão Geral & Administrativo": {
                    "email": "gnldburgos@gmail.com",
                    "nome": "Genildo Burgos",
                    "cargo": "GERENTE",
                    "crmv": None
                },
                "Carla Mendonça — Coordenação de Estética & Banho": {
                    "email": "carla.tosa@gmail.com",
                    "nome": "Carla Mendonça",
                    "cargo": "TOSADOR",
                    "crmv": None
                },
                "Fernanda Duarte — Atendimento & Frente de Caixa": {
                    "email": "fernanda.caixa@gmail.com",
                    "nome": "Fernanda Duarte",
                    "cargo": "RECEPCIONISTA",
                    "crmv": None
                },
                "Dr. Assuero Ximenes — Conselho & Auditoria Médica": {
                    "email": "assuero.ximenes@ufape.edu.br",
                    "nome": "Dr. Assuero Ximenes",
                    "cargo": "GERENTE",
                    "crmv": None
                }
            }

            perfil_escolhido = st.selectbox(
                "Selecionar Profissional / Cargo",
                list(perfis.keys()),
                label_visibility="collapsed"
            )

            senha_acesso = st.text_input(
                "Chave de Acesso / PIN",
                type="password",
                value="••••••••",
                help="Acesso padrão de estação corporativa liberado para demonstração"
            )

            st.write("")
            if st.button("Entrar no PetFlow ERP", type="primary", use_container_width=True):
                info = perfis[perfil_escolhido]
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = info
                st.session_state["simulated_persona_email"] = info["email"]
                st.rerun()

        with tab_google:
            st.caption("Autenticação com e-mail corporativo via Google Cloud Identity:")
            
            try:
                google_user_email = AuthManager.get_google_sso_email()
            except Exception:
                google_user_email = None
            
            if google_user_email:
                st.success(f"Sessão Google detectada: **{google_user_email}**")
                if st.button("Continuar com esta Conta", type="primary", use_container_width=True):
                    st.session_state["authenticated"] = True
                    st.session_state["simulated_persona_email"] = google_user_email
                    st.session_state["current_user"] = None
                    st.rerun()
            else:
                st.info("Para login via SSO, acesse com conta vinculada ao Google Workspace da clínica.")
                st.button("🔑 Autenticar com Google", use_container_width=True, disabled=True, help="Disponível quando o aplicativo é acessado com Viewer Auth configurado no Streamlit Cloud.")

        st.markdown(
            """
                <div class="login-footer">
                    PetFlow Enterprise Edition • Build 2026.2-PROD<br>
                    Infraestrutura em Nuvem Supabase Postgres 17
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
