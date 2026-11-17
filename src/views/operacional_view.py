import streamlit as st
import pandas as pd
import urllib.parse
from src.services.atendimento_service import AtendimentoService
from src.services.cadastro_service import CadastroService

def render_operacional_view():
    st.title("⚡ Atendimento Operacional")
    st.caption("Módulos Integrados de Atendimento: Estética Pet com Check-in Visual de Segurança e Consultório Veterinário com Prontuário Clínico.")

    tabs = st.tabs(["🛁 Estética (Banho & Tosa)", "🩺 Consultório Veterinário (Prontuário Clínico)"])

    # =========================================================================
    # TAB 1: ESTÉTICA (BANHO & TOSA)
    # =========================================================================
    with tabs[0]:
        st.subheader("Esteira Operacional de Banho & Tosa")

        sub_tab1, sub_tab2 = st.tabs(["📋 Fila & Gestão de Status", "➕ Novo Check-in de Entrada"])

        with sub_tab2:
            st.markdown("#### 📸 Check-in Visual de Segurança (Mitigação de Litígios)")
            st.caption("Registre o estado de entrada do pet para resguardar o profissional e a clínica de reclamações prévias.")

            with st.form("form_novo_checkin", clear_on_submit=True):
                try:
                    animais = CadastroService.listar_animais()
                    servicos_estetica = CadastroService.listar_servicos(tipo_servico="ESTETICA")
                    profissionais = CadastroService.listar_colaboradores()
                except Exception as e:
                    animais, servicos_estetica, profissionais = [], [], []
                    st.error(f"Erro ao carregar dados: {e}")

                dict_animais = {f"{a['nome']} ({a['codigo_prontuario']} - Tutor: {a['tutor_nome']})": a["id"] for a in animais}
                dict_servicos = {f"{s['nome']} - R$ {float(s['preco_base']):.2f}": s["id"] for s in servicos_estetica}
                dict_profs = {f"{c['nome']} ({c['cargo']})": c["id"] for c in profissionais if c["cargo"] in ("TOSADOR", "BANHISTA", "GERENTE")}

                c1, c2 = st.columns(2)
                with c1:
                    pet_sel = st.selectbox("Animal *", options=list(dict_animais.keys())) if dict_animais else None
                    serv_sel = st.selectbox("Serviço Solicitado *", options=list(dict_servicos.keys())) if dict_servicos else None
                with c2:
                    prof_sel = st.selectbox("Profissional Responsável *", options=list(dict_profs.keys())) if dict_profs else None
                    foto_url = st.text_input("URL da Foto do Pet na Entrada (Opcional)", placeholder="https://...")

                st.markdown("**Inspeção Física de Entrada:**")
                ch1, ch2, ch3 = st.columns(3)
                with ch1:
                    tem_pulgas = st.checkbox("Presença de Pulgas / Carrapatos", value=False)
                with ch2:
                    tem_nos = st.checkbox("Nós Severos na Pelagem", value=False)
                with ch3:
                    tem_ferimento = st.checkbox("Ferimento / Lesão Prévia", value=False)

                obs_manejo = st.text_area("Observações de Manejo / Comportamento", placeholder="Ex: Animal idoso, muito agitado, sensível à tesoura perto dos olhos...")

                submitted_checkin = st.form_submit_button("Realizar Check-in & Iniciar Atendimento", use_container_width=True)
                if submitted_checkin:
                    if not pet_sel or not serv_sel or not prof_sel:
                        st.error("Selecione o Animal, o Serviço e o Profissional.")
                    else:
                        try:
                            res_os = AtendimentoService.criar_atendimento_estetica(
                                animal_id=dict_animais[pet_sel],
                                servico_id=dict_servicos[serv_sel],
                                colaborador_id=dict_profs[prof_sel],
                                tem_pulgas=tem_pulgas,
                                tem_nos_pelagem=tem_nos,
                                tem_ferimento_previo=tem_ferimento,
                                foto_checkin_url=foto_url,
                                observacoes_manejo=obs_manejo
                            )
                            st.success(f"Check-in realizado com sucesso! Ordem de Serviço gerada: **{res_os['numero_os']}**")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao registrar check-in: {e}")

        with sub_tab1:
            st.markdown("#### Fila de Banho e Tosa em Tempo Real")
            try:
                atendimentos = AtendimentoService.listar_atendimentos_estetica_dia()
                if not atendimentos:
                    st.info("Nenhum atendimento na fila de hoje.")
                else:
                    for at in atendimentos:
                        status_cor = {
                            "RECEBIDO_CHECKIN": "orange",
                            "EM_BANHO": "blue",
                            "EM_TOSA": "violet",
                            "PRONTO_AVISAR": "green",
                            "FINALIZADO_ENTREGUE": "gray"
                        }.get(at["status"], "gray")

                        with st.container(border=True):
                            col_info, col_status, col_acao = st.columns([4, 3, 3])
                            with col_info:
                                st.markdown(f"### :{status_cor}[{at['numero_os']}] — **{at['animal_nome']}** ({at['codigo_prontuario']})")
                                st.markdown(f"**Tutor:** {at['tutor_nome']} • **Serviço:** {at['servico_nome']} • **Profissional:** {at['profissional_nome']}")
                                flags = []
                                if at["tem_pulgas"]: flags.append("⚠️ Pulgas")
                                if at["tem_nos_pelagem"]: flags.append("✂️ Nós na pelagem")
                                if at["tem_ferimento_previo"]: flags.append("🩹 Ferimento prévio")
                                if flags:
                                    st.warning(" | ".join(flags))

                            with col_status:
                                st.markdown(f"**Status Atual:** `{at['status']}`")
                                novo_st = st.selectbox(
                                    "Avançar Etapa:",
                                    ["RECEBIDO_CHECKIN", "EM_BANHO", "EM_TOSA", "PRONTO_AVISAR", "FINALIZADO_ENTREGUE"],
                                    index=["RECEBIDO_CHECKIN", "EM_BANHO", "EM_TOSA", "PRONTO_AVISAR", "FINALIZADO_ENTREGUE"].index(at["status"]),
                                    key=f"status_os_{at['id']}"
                                )
                                if st.button("Atualizar Status", key=f"btn_up_{at['id']}"):
                                    AtendimentoService.atualizar_status_estetica(at["id"], novo_st)
                                    st.success(f"Status atualizado para {novo_st}!")
                                    st.rerun()

                            with col_acao:
                                # Gerador de WhatsApp com 1 clique
                                telefone_limpo = "".join(filter(str.isdigit, at["tutor_whatsapp"] or ""))
                                if not telefone_limpo.startswith("55"):
                                    telefone_limpo = "55" + telefone_limpo

                                msg_wpp = f"Olá {at['tutor_nome']}! Seu pet {at['animal_nome']} está prontinho e cheiroso(a) aqui no PetFlow! 🐾 Pode vir buscá-lo!"
                                link_wpp = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(msg_wpp)}"
                                
                                st.link_button("📲 Avisar no WhatsApp", link_wpp, use_container_width=True)
                                st.caption(f"Valor: R$ {float(at['valor_servico']):.2f} (Comissão: R$ {float(at['valor_comissao']):.2f})")
            except Exception as e:
                st.error(f"Erro ao listar fila: {e}")

    # =========================================================================
    # TAB 2: CONSULTÓRIO CLÍNICO (PRONTUÁRIO MÉDICO ELETRÔNICO)
    # =========================================================================
    with tabs[1]:
        st.subheader("Atendimento Veterinário Especializado")
        st.caption("Prontuário clínico estruturado com histórico médico, avaliação de sinais vitais e receituário.")

        sub_c1, sub_c2 = st.tabs(["➕ Nova Consulta Clínica", "📋 Histórico de Consultas"])

        with sub_c1:
            st.markdown("#### Registro de Atendimento Clínico & Prescrição")
            with st.form("form_nova_consulta", clear_on_submit=True):
                try:
                    animais_clin = CadastroService.listar_animais()
                    veterinarios = CadastroService.listar_colaboradores(cargo="VETERINARIO")
                    medicamentos = CadastroService.listar_medicamentos()
                    vacinas_insumos = CadastroService.listar_produtos()
                except Exception as e:
                    animais_clin, veterinarios, medicamentos, vacinas_insumos = [], [], [], []
                    st.error(f"Erro ao carregar dados: {e}")

                dict_pets_clin = {f"{a['nome']} ({a['codigo_prontuario']} - {a['tutor_nome']})": a for a in animais_clin}
                dict_vets = {f"Dr(a). {v['nome']} ({v['crmv']})": v["id"] for v in veterinarios}

                col_cl1, col_cl2 = st.columns(2)
                with col_cl1:
                    pet_clin_sel = st.selectbox("Paciente Animal *", options=list(dict_pets_clin.keys())) if dict_pets_clin else None
                    tipo_consulta = st.selectbox("Tipo de Consulta *", ["PRIMEIRA_VEZ", "RETORNO"])
                with col_cl2:
                    vet_sel = st.selectbox("Médico Veterinário Responsável *", options=list(dict_vets.keys())) if dict_vets else None
                    peso_atual = st.number_input("Peso Atual (kg) *", min_value=0.1, max_value=120.0, value=7.5, step=0.1)

                st.markdown("---")
                st.markdown("##### 📝 Anamnese Clínica Completa")
                queixa = st.text_area("Queixa Principal *", placeholder="Ex: Animal prostrado há 2 dias, episódios de vômito e recusa de ração.")
                col_an1, col_an2 = st.columns(2)
                with col_an1:
                    alimentacao = st.text_input("Dieta / Alimentação Habitual", value="Ração comercial Super Premium")
                with col_an2:
                    alteracoes = st.text_input("Alterações Observadas pelo Tutor", placeholder="Ex: Ingestão de corpo estranho suspeita")

                st.markdown("---")
                st.markdown("##### 🩺 Avaliação Físico Geral e Sinais Vitais")
                v1, v2, v3, v4 = st.columns(4)
                with v1:
                    temp = st.number_input("Temperatura (°C)", min_value=35.0, max_value=43.0, value=38.6, step=0.1)
                with v2:
                    fc = st.number_input("Freq. Cardíaca (bpm)", min_value=40, max_value=250, value=110, step=5)
                with v3:
                    fr = st.number_input("Freq. Respiratória (mpm)", min_value=10, max_value=100, value=24, step=2)
                with v4:
                    tpc = st.number_input("TPC (Segundos)", min_value=1, max_value=6, value=2, step=1)

                parecer = st.text_area("Parecer Diagnóstico & Conduta Médica", placeholder="Ex: Suspeita de gastroenterite aguda. Instituída fluidoterapia e antibioticoterapia.")

                st.markdown("---")
                st.markdown("##### 💊 Prescrição Médica & Receituário")
                dict_meds = {f"{m['nome']} ({m['principio_ativo']} - {m['concentracao']})": m["id"] for m in medicamentos}
                
                c_rx1, c_rx2, c_rx3 = st.columns(3)
                with c_rx1:
                    med_sel = st.selectbox("Medicamento (Catálogo)", options=["Nenhum"] + list(dict_meds.keys()))
                with c_rx2:
                    dose = st.text_input("Posologia / Dose", placeholder="Ex: 1 comp. a cada 12h")
                with c_rx3:
                    periodo = st.number_input("Duração (Dias)", min_value=1, max_value=90, value=7)

                st.markdown("---")
                st.markdown("##### 💉 Vacina / Insumo Aplicado na Consulta (Baixa Imediata de Estoque)")
                insumos_options = {f"{p['nome']} (Saldo: {p['estoque_atual']} {p['unidade_medida']})": p["id"] for p in vacinas_insumos if p["tipo_produto"] in ("INSUMO_OPERACIONAL", "AMBOS")}
                c_vac1, c_vac2 = st.columns([3, 1])
                with c_vac1:
                    vac_sel = st.selectbox("Insumo / Vacina Consumida", options=["Nenhum"] + list(insumos_options.keys()))
                with c_vac2:
                    qtd_vac = st.number_input("Quantidade Consumida", min_value=0.0, value=1.0, step=1.0)

                st.markdown("---")
                col_fin1, col_fin2 = st.columns(2)
                with col_fin1:
                    valor_consulta = st.number_input("Valor da Consulta (R$) *", min_value=0.0, value=150.0, step=10.0)
                with col_fin2:
                    pct_comissao_vet = st.number_input("Comissão Médica (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0)

                submitted_consulta = st.form_submit_button("Salvar Prontuário & Concluir Consulta", use_container_width=True)
                if submitted_consulta:
                    if not pet_clin_sel or not vet_sel or not queixa:
                        st.error("Preencha o Paciente, o Veterinário e a Queixa Principal.")
                    else:
                        try:
                            # Monta prescrição
                            prescricoes = []
                            if med_sel != "Nenhum" and dose:
                                prescricoes.append({
                                    "medicamento_id": dict_meds[med_sel],
                                    "dose": dose,
                                    "frequencia": "Conforme prescrito",
                                    "periodo_dias": periodo,
                                    "observacoes": "Uso oral"
                                })

                            # Monta insumos
                            insumos = []
                            if vac_sel != "Nenhum" and qtd_vac > 0:
                                insumos.append({
                                    "produto_id": insumos_options[vac_sel],
                                    "quantidade": qtd_vac
                                })

                            res_cons = AtendimentoService.criar_consulta_veterinaria(
                                animal_id=dict_pets_clin[pet_clin_sel]["id"],
                                veterinario_id=dict_vets[vet_sel],
                                peso_atual=peso_atual,
                                tipo_consulta=tipo_consulta,
                                queixa_principal=queixa,
                                alteracoes_clinicas=alteracoes,
                                suspeitas_clinicas="",
                                alimentacao=alimentacao,
                                temperatura=temp,
                                frequencia_cardiaca=fc,
                                frequencia_respiratoria=fr,
                                tpc=tpc,
                                parecer_diagnostico=parecer,
                                valor_consulta=valor_consulta,
                                percentual_comissao=pct_comissao_vet,
                                prescricoes_lista=prescricoes,
                                insumos_consumidos=insumos
                            )
                            st.success(f"Consulta gravada com sucesso! Código: **{res_cons['numero_consulta']}**. O valor de R$ {valor_consulta:.2f} já está disponível para recebimento no PDV.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar consulta: {e}")

        with sub_c2:
            st.markdown("#### Histórico de Prontuários Médicos")
            try:
                consultas = AtendimentoService.listar_consultas_recentes(limit=50)
                if consultas:
                    df_c = pd.DataFrame([
                        {
                            "Consulta": c["numero_consulta"],
                            "Data": pd.to_datetime(c["data_consulta"]).strftime("%d/%m/%Y %H:%M"),
                            "Animal": f"{c['animal_nome']} ({c['codigo_prontuario']})",
                            "Tutor": c["tutor_nome"],
                            "Veterinário": f"Dr(a). {c['veterinario_nome']} ({c['crmv']})",
                            "Queixa": c["queixa_principal"],
                            "Valor": f"R$ {float(c['valor_consulta']):.2f}",
                            "Status": c["status"]
                        }
                        for c in consultas
                    ])
                    st.dataframe(df_c, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma consulta médica realizada até o momento.")
            except Exception as e:
                st.error(f"Erro ao carregar prontuários: {e}")

if __name__ == "__main__":
    render_operacional_view()
