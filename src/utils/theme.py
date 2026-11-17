import streamlit as st

def apply_enterprise_theme():
    """
    Injeta regras de design system boutique SaaS para transformar a estética
    do Streamlit em uma aplicação de mercado refinada e elegante.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* Tipografia global */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #0F172A;
            background-color: #F8FAFC;
        }

        /* Espaçamento superior mais elegante */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1280px;
        }

        /* Barra Lateral Moderna */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02) !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0.5rem !important;
        }

        /* Cards customizados PetFlow */
        .pf-metric-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
            transition: all 0.2s ease;
        }
        .pf-metric-card:hover {
            box-shadow: 0 4px 12px 0 rgba(15, 23, 42, 0.08);
            border-color: #CBD5E1;
        }
        .pf-metric-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748B;
            margin-bottom: 6px;
        }
        .pf-metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.5px;
        }
        .pf-metric-helper {
            font-size: 12px;
            color: #0D9488;
            margin-top: 4px;
            font-weight: 500;
        }

        /* Botões customizados */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 8px 16px !important;
            transition: all 0.15s ease !important;
            border: 1px solid #CBD5E1 !important;
        }
        .stButton > button:hover {
            border-color: #0D9488 !important;
            color: #0D9488 !important;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"] {
            background: #0D9488 !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(13, 148, 136, 0.2) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #0F766E !important;
            box-shadow: 0 4px 8px rgba(13, 148, 136, 0.3) !important;
        }

        /* Abas Elegantes */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid #E2E8F0;
            padding-bottom: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px 6px 0 0 !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            color: #64748B !important;
            border: none !important;
            background-color: transparent !important;
        }
        .stTabs [aria-selected="true"] {
            color: #0D9488 !important;
            border-bottom: 2px solid #0D9488 !important;
            background-color: transparent !important;
        }

        /* Dataframes refinados */
        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }

        /* Badges de Status Operacional */
        .badge-status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-green { background: #ECFDF5; color: #059669; }
        .badge-blue { background: #EFF6FF; color: #2563EB; }
        .badge-yellow { background: #FEF3C7; color: #D97706; }
        .badge-purple { background: #F5F3FF; color: #7C3AED; }
        .badge-gray { background: #F1F5F9; color: #64748B; }

        /* Rodapé discreto */
        footer { visibility: hidden; }
        header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True
    )
