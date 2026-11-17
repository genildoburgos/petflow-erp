import streamlit as st
import pandas as pd
from datetime import datetime
from src.auth.auth_manager import AuthManager
from src.database.connection import test_connection
from src.services.atendimento_service import AtendimentoService
from src.services.estoque_service import EstoqueService
from src.services.financeiro_service import FinanceiroService

def render_home_view():
    """
    Painel Executivo PetFlow ERP — Design System Boutique SaaS.
    Central de monitoramento em tempo real com estética moderna e humanizada.
    """
    colaborador = AuthManager.get_current_colaborador()
    primeiro_nome = colaborador.get("nome", "Operador").split()[0]
    data_formatada = datetime.now().strftime("%d de %B de %Y").replace(
        "January", "Janeiro"
    ).replace("February", "Fevereiro").replace("March", "Março").replace("April", "Abril"
    ).replace("May", "Maio").replace("June", "Junho").replace("July", "Julho"
    ).replace("August", "Agosto").replace("September", "Setembro").replace("October", "Outubro"
    ).replace("November", "Novembro").replace("December", "Dezembro")

    # Header Executivo com Saudação Humanizada e Status Operacional
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius: 16px; padding: 26px 30px; margin-bottom: 24px; color: #FFFFFF; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08);">
            <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #14B8A6; margin-bottom: 6px;">
                    Painel Executivo • PetFlow Enterprise
                </div>
                <div style="font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">
                    Olá, {primeiro_nome}! 👋
                </div>
                <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                    {data_formatada} • Panorama operacional e financeiro da unidade em tempo real.
                </div>
            </div>
            <div style="text-align: right; background: rgba(255, 255, 255, 0.06); padding: 12px 18px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="font-size: 11px; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.5px;">Status da Unidade</div>
                <div style="font-size: 13px; font-weight: 700; color: #34D399; margin-top: 2px;">🟢 Operação Normal</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Carregamento Seguro dos Indicadores
    try:
        estetica_hoje = AtendimentoService.listar_atendimentos_estetica_dia()
        qtd_estetica = len(estetica_hoje)
    except Exception:
        estetica_hoje = []
        qtd_estetica = 0

    try:
        consultas_recentes = AtendimentoService.listar_consultas_recentes(limit=5)
        qtd_consultas = len(consultas_recentes)
    except Exception:
        consultas_recentes = []
        qtd_consultas = 0

    try:
        prods_criticos = EstoqueService.listar_posicao_estoque(apenas_criticos=True)
        qtd_criticos = len(prods_criticos)
    except Exception:
        prods_criticos = []
        qtd_criticos = 0

    try:
        resumo_fin = FinanceiroService.obter_resumo_caixa()
        saldo_caixa = resumo_fin.get("saldo_realizado", 0.0)
    except Exception:
        saldo_caixa = 0.0

    # 2. Métricas de Topo em Cards Refinados
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f"""
            <div class="pf-metric-card">
                <div class="pf-metric-label">🛁 Estética & Banhos Hoje</div>
                <div class="pf-metric-value">{qtd_estetica} <span style="font-size: 15px; font-weight: 500; color: #64748B;">pets</span></div>
                <div class="pf-metric-helper">Check-ins e fila do dia</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        saldo_formatado = f"R$ {saldo_caixa:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(
            f"""
            <div class="pf-metric-card">
                <div class="pf-metric-label">💵 Caixa Líquido Realizado</div>
                <div class="pf-metric-value">{saldo_formatado}</div>
                <div class="pf-metric-helper">Recebimentos consolidados</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            f"""
            <div class="pf-metric-card">
                <div class="pf-metric-label">🩺 Consultas & Prontuários</div>
                <div class="pf-metric-value">{qtd_consultas} <span style="font-size: 15px; font-weight: 500; color: #64748B;">atendimentos</span></div>
                <div class="pf-metric-helper">Consultório clínico ativo</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m4:
        cor_alerta = "#EF4444" if qtd_criticos > 0 else "#10B981"
        sub_alerta = "Reposição imediata recomendada" if qtd_criticos > 0 else "Níveis de estoque normais"
        st.markdown(
            f"""
            <div class="pf-metric-card">
                <div class="pf-metric-label">📦 Estoque em Atenção</div>
                <div class="pf-metric-value" style="color: {cor_alerta};">{qtd_criticos} <span style="font-size: 15px; font-weight: 500; color: #64748B;">itens</span></div>
                <div class="pf-metric-helper" style="color: {cor_alerta};">{sub_alerta}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # 3. Layout Principal: Fluxo Operacional & Ações Rápidas
    col_main, col_side = st.columns([7, 3])

    with col_main:
        # Seção Banho & Tosa
        st.markdown("#### 📋 Fila Operacional de Estética (Hoje)")
        if estetica_hoje:
            df_est = pd.DataFrame([
                {
                    "OS": item["numero_os"],
                    "Paciente": f"{item['animal_nome']} ({item.get('codigo_prontuario', 'S/N')})",
                    "Tutor": item["tutor_nome"],
                    "Serviço": item["servico_nome"],
                    "Status": item["status"],
                    "Profissional": item["profissional_nome"],
                    "Inspeção": ("⚠️ Pulgas " if item.get("tem_pulgas") else "") + 
                                ("✂️ Nós " if item.get("tem_nos_pelagem") else "") + 
                                ("🩹 Ferimento " if item.get("tem_ferimento_previo") else "") or "✅ Normal"
                }
                for item in estetica_hoje
            ])
            st.dataframe(df_est, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 24px; text-align: center; color: #64748B;">
                    <div style="font-size: 28px; margin-bottom: 8px;">🛁</div>
                    <div style="font-weight: 600; color: #334155;">Nenhum atendimento na fila de estética hoje</div>
                    <div style="font-size: 12px; margin-top: 4px;">Utilize o menu <strong>Atendimento Clínico & Estética</strong> para registrar a entrada de novos pets com fotos e checklist de inspeção.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")
        # Seção Consultas Clínicas Recentes
        st.markdown("#### 🩺 Prontuários Clínicos Recentes")
        if consultas_recentes:
            df_cons = pd.DataFrame([
                {
                    "Prontuário": item["codigo_prontuario"],
                    "Paciente": item["animal_nome"],
                    "Tutor": item["tutor_nome"],
                    "Veterinário(a)": f"Dr(a). {item['veterinario_nome']}",
                    "Queixa Principal": item["queixa_principal"][:45] + "..." if len(item["queixa_principal"]) > 45 else item["queixa_principal"],
                    "Honorário": f"R$ {float(item['valor_consulta']):.2f}"
                }
                for item in consultas_recentes
            ])
            st.dataframe(df_cons, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 24px; text-align: center; color: #64748B;">
                    <div style="font-size: 28px; margin-bottom: 8px;">🩺</div>
                    <div style="font-weight: 600; color: #334155;">Nenhum prontuário registrado recentemente</div>
                    <div style="font-size: 12px; margin-top: 4px;">Registre avaliações físicas completas, anamnese e prescrições no consultório veterinário.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_side:
        # Ações Rápidas
        st.markdown("#### ⚡ Ações Rápidas")
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                <div style="font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 12px;">Atalhos de Alta Produtividade:</div>
                <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; color: #334155;">
                    <div style="padding: 10px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                        🛒 <strong>Frente de Caixa (PDV)</strong><br>
                        <span style="font-size: 11px; color: #64748B;">Emita vendas rápidas de balcão e receba pagamentos</span>
                    </div>
                    <div style="padding: 10px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                        🛁 <strong>Novo Check-in Estética</strong><br>
                        <span style="font-size: 11px; color: #64748B;">Entrada de pet com fotos e inspeção prévia de segurança</span>
                    </div>
                    <div style="padding: 10px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                        🩺 <strong>Nova Consulta Médica</strong><br>
                        <span style="font-size: 11px; color: #64748B;">Exame físico, anamnese e receituário digital</span>
                    </div>
                    <div style="padding: 10px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                        📥 <strong>Entrada de Mercadoria / NF</strong><br>
                        <span style="font-size: 11px; color: #64748B;">Registro de notas fiscais com atualização de estoque</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Alertas de Reposição de Estoque
        st.markdown("#### 📦 Reposição de Insumos")
        if prods_criticos:
            for p in prods_criticos[:5]:
                st.markdown(
                    f"""
                    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                        <div style="font-size: 13px; font-weight: 700; color: #991B1B;">{p['nome']}</div>
                        <div style="font-size: 11px; color: #B91C1C; margin-top: 2px;">
                            Saldo atual: <strong>{p['estoque_atual']} {p['unidade_medida']}</strong> (Mínimo: {p['estoque_minimo']})
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 10px; padding: 14px; color: #065F46; font-size: 12px; font-weight: 600;">
                    ✅ Todos os insumos e medicamentos estão com saldo seguro acima do ponto de pedido.
                </div>
                """,
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    render_home_view()
