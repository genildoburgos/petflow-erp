import streamlit as st
import pandas as pd
from src.services.cadastro_service import CadastroService

def render_cadastros_view():
    st.title("🗂️ Cadastros Mestres")
    st.caption("Gestão de entidades estruturais alinhadas aos requisitos acadêmicos e ao padrão de domínio clínico HVU.")

    tabs = st.tabs(["🐶 Animais", "👤 Tutores", "📦 Produtos", "✂️ Serviços", "👨‍⚕️ Colaboradores", "🏭 Fornecedores"])

    # =========================================================================
    # TAB 1: ANIMAIS
    # =========================================================================
    with tabs[0]:
        st.subheader("Cadastro & Prontuário de Animais")
        
        col_list, col_form = st.columns([3, 2])
        
        with col_form:
            st.markdown("#### ➕ Novo Animal")
            with st.form("form_novo_animal", clear_on_submit=True):
                # Carrega tutores e raças
                try:
                    tutores = CadastroService.listar_tutores()
                    racas = CadastroService.listar_racas()
                except Exception as e:
                    tutores, racas = [], []
                    st.error(f"Erro ao carregar dados: {e}")

                dict_tutores = {f"{t['nome']} ({t['cpf'] or t['telefone']})": t["id"] for t in tutores}
                dict_racas = {f"{r['nome']} ({r['especie_nome']} - {r['porte']})": r["id"] for r in racas}

                if not dict_tutores:
                    st.warning("Cadastre ao menos um tutor primeiro na aba 'Tutores'.")
                
                tutor_sel = st.selectbox("Tutor Responsável *", options=list(dict_tutores.keys())) if dict_tutores else None
                raca_sel = st.selectbox("Raça / Espécie / Porte *", options=list(dict_racas.keys())) if dict_racas else None
                
                c_a, c_b = st.columns(2)
                with c_a:
                    nome_animal = st.text_input("Nome do Animal *")
                    sexo = st.selectbox("Sexo *", ["M", "F"], format_func=lambda x: "Macho" if x == "M" else "Fêmea")
                with c_b:
                    peso = st.number_input("Peso (kg) *", min_value=0.1, max_value=120.0, value=5.0, step=0.1)
                    castrado = st.checkbox("Castrado?", value=False)

                alergias = st.text_area("Alergias / Condições Especiais", placeholder="Ex: Alergia a dipirona, dermatite atópica...")
                foto_url = st.text_input("URL da Foto (Opcional)")

                submitted_animal = st.form_submit_button("Cadastrar Animal", use_container_width=True)
                if submitted_animal:
                    if not nome_animal or not tutor_sel or not raca_sel:
                        st.error("Preencha todos os campos obrigatórios (*).")
                    else:
                        try:
                            novo_pet = CadastroService.criar_animal(
                                tutor_id=dict_tutores[tutor_sel],
                                raca_id=dict_racas[raca_sel],
                                nome=nome_animal,
                                sexo=sexo,
                                peso=peso,
                                castrado=castrado,
                                alergias=alergias,
                                foto_url=foto_url
                            )
                            st.success(f"Animal cadastrado com sucesso! Prontuário: **{novo_pet['codigo_prontuario']}**")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar animal: {e}")

        with col_list:
            st.markdown("#### 🔍 Animais Cadastrados")
            busca_pet = st.text_input("Buscar por nome, prontuário ou tutor:", placeholder="Digite para filtrar...")
            try:
                animais = CadastroService.listar_animais(termo_busca=busca_pet)
                if animais:
                    df_animais = pd.DataFrame([
                        {
                            "Prontuário": a["codigo_prontuario"],
                            "Nome": a["nome"],
                            "Espécie/Raça": f"{a['especie_nome']} - {a['raca_nome']} ({a['porte']})",
                            "Tutor": a["tutor_nome"],
                            "Sexo": "Macho" if a["sexo"] == "M" else "Fêmea",
                            "Peso (kg)": float(a["peso"]),
                            "Castrado": "Sim" if a["castrado"] else "Não",
                            "Alergias": a["alergias"] or "Nenhuma"
                        }
                        for a in animais
                    ])
                    st.dataframe(df_animais, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum animal cadastrado ou correspondente à busca.")
            except Exception as e:
                st.error(f"Erro ao listar animais: {e}")

    # =========================================================================
    # TAB 2: TUTORES (CLIENTES)
    # =========================================================================
    with tabs[1]:
        st.subheader("Cadastro de Tutores (Clientes)")
        col_t_list, col_t_form = st.columns([3, 2])

        with col_t_form:
            st.markdown("#### ➕ Novo Tutor")
            with st.form("form_novo_tutor", clear_on_submit=True):
                nome_tutor = st.text_input("Nome Completo *")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    telefone = st.text_input("Telefone / WhatsApp *", placeholder="(87) 99999-0000")
                    cpf = st.text_input("CPF (Opcional)", placeholder="000.000.000-00")
                with col_t2:
                    email = st.text_input("E-mail (Opcional)")
                    rg = st.text_input("RG (Opcional)")

                st.markdown("**Endereço (Padrão Normalizado HVU):**")
                col_e1, col_e2 = st.columns([2, 1])
                with col_e1:
                    rua = st.text_input("Rua / Logradouro", value="Av. Rui Barbosa")
                    bairro = st.text_input("Bairro", value="Heliópolis")
                with col_e2:
                    numero = st.text_input("Número", value="100")
                    cep = st.text_input("CEP", value="55295-000")

                cidade = st.text_input("Cidade / UF", value="Garanhuns - PE", disabled=True)
                observacoes = st.text_area("Observações Cadastrais")

                submitted_tutor = st.form_submit_button("Cadastrar Tutor", use_container_width=True)
                if submitted_tutor:
                    if not nome_tutor or not telefone:
                        st.error("Nome e Telefone são obrigatórios.")
                    else:
                        try:
                            tid = CadastroService.criar_tutor(
                                nome=nome_tutor,
                                telefone=telefone,
                                cpf=cpf,
                                email=email,
                                rg=rg,
                                observacoes=observacoes,
                                cep=cep,
                                rua=rua,
                                numero=numero,
                                bairro=bairro,
                                cidade="Garanhuns",
                                uf="PE"
                            )
                            st.success(f"Tutor cadastrado com sucesso! ID: {tid}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar tutor: {e}")

        with col_t_list:
            st.markdown("#### 🔍 Tutores Cadastrados")
            busca_tutor = st.text_input("Buscar por nome, CPF ou telefone:", key="busca_tutor")
            try:
                tutores = CadastroService.listar_tutores(termo_busca=busca_tutor)
                if tutores:
                    df_tutores = pd.DataFrame([
                        {
                            "ID": t["id"],
                            "Nome": t["nome"],
                            "WhatsApp": t["telefone"],
                            "CPF": t["cpf"] or "Não informado",
                            "Bairro": t["bairro"] or "-",
                            "Cidade": f"{t['cidade'] or 'Garanhuns'}"
                        }
                        for t in tutores
                    ])
                    st.dataframe(df_tutores, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum tutor encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar tutores: {e}")

    # =========================================================================
    # TAB 3: PRODUTOS (REVENDA & INSUMOS)
    # =========================================================================
    with tabs[2]:
        st.subheader("Catálogo de Produtos & Insumos Operacionais")
        col_p_list, col_p_form = st.columns([3, 2])

        with col_p_form:
            st.markdown("#### ➕ Novo Produto")
            with st.form("form_novo_produto", clear_on_submit=True):
                try:
                    categorias_prod = CadastroService.listar_categorias(tipo="PRODUTO")
                    dict_cat_prod = {c["nome"]: c["id"] for c in categorias_prod}
                except Exception:
                    dict_cat_prod = {}

                cat_sel = st.selectbox("Categoria *", options=list(dict_cat_prod.keys())) if dict_cat_prod else None
                nome_prod = st.text_input("Nome do Produto *")
                codigo_barras = st.text_input("Código de Barras (EAN)")
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    tipo_prod = st.selectbox("Finalidade *", ["REVENDA", "INSUMO_OPERACIONAL", "AMBOS"])
                    unidade = st.selectbox("Unidade *", ["UN", "KG", "L", "ML", "DOSE", "PCT"])
                with col_p2:
                    preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, value=10.0, step=0.5)
                    preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, value=20.0, step=0.5)

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    est_min = st.number_input("Estoque Mínimo", min_value=0.0, value=5.0, step=1.0)
                with col_e2:
                    est_ini = st.number_input("Estoque Inicial", min_value=0.0, value=10.0, step=1.0)

                submitted_prod = st.form_submit_button("Cadastrar Produto", use_container_width=True)
                if submitted_prod:
                    if not nome_prod or not cat_sel:
                        st.error("Nome e Categoria são obrigatórios.")
                    else:
                        try:
                            pid = CadastroService.criar_produto(
                                categoria_id=dict_cat_prod[cat_sel],
                                nome=nome_prod,
                                tipo_produto=tipo_prod,
                                unidade_medida=unidade,
                                preco_custo=preco_custo,
                                preco_venda=preco_venda,
                                estoque_minimo=est_min,
                                estoque_inicial=est_ini,
                                codigo_barras=codigo_barras
                            )
                            st.success(f"Produto cadastrado com sucesso! ID: {pid}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar produto: {e}")

        with col_p_list:
            st.markdown("#### 🔍 Produtos Cadastrados")
            try:
                produtos = CadastroService.listar_produtos()
                if produtos:
                    df_prod = pd.DataFrame([
                        {
                            "ID": p["id"],
                            "Nome": p["nome"],
                            "Categoria": p["categoria_nome"],
                            "Tipo": p["tipo_produto"],
                            "Estoque Atual": f"{p['estoque_atual']} {p['unidade_medida']}",
                            "Est. Mínimo": f"{p['estoque_minimo']} {p['unidade_medida']}",
                            "Custo": f"R$ {float(p['preco_custo']):.2f}",
                            "Venda": f"R$ {float(p['preco_venda']):.2f}",
                            "Status": "⚠️ Baixo" if p["estoque_critico"] else "✅ OK"
                        }
                        for p in produtos
                    ])
                    st.dataframe(df_prod, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum produto cadastrado.")
            except Exception as e:
                st.error(f"Erro ao carregar produtos: {e}")

    # =========================================================================
    # TAB 4: SERVIÇOS
    # =========================================================================
    with tabs[3]:
        st.subheader("Catálogo de Serviços (Estética & Clínico)")
        col_s_list, col_s_form = st.columns([3, 2])

        with col_s_form:
            st.markdown("#### ➕ Novo Serviço")
            with st.form("form_novo_servico", clear_on_submit=True):
                try:
                    categorias_serv = CadastroService.listar_categorias(tipo="SERVICO")
                    dict_cat_serv = {c["nome"]: c["id"] for c in categorias_serv}
                except Exception:
                    dict_cat_serv = {}

                cat_serv_sel = st.selectbox("Categoria *", options=list(dict_cat_serv.keys())) if dict_cat_serv else None
                nome_serv = st.text_input("Nome do Serviço *")
                tipo_serv = st.selectbox("Tipo de Serviço *", ["ESTETICA", "CLINICO"])
                
                col_sv1, col_sv2 = st.columns(2)
                with col_sv1:
                    preco_base = st.number_input("Preço Base (R$) *", min_value=0.0, value=60.0, step=5.0)
                    duracao = st.number_input("Duração (Minutos)", min_value=15, max_value=360, value=60, step=15)
                with col_sv2:
                    comissao_pct = st.number_input("Comissão Padrão (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)

                submitted_serv = st.form_submit_button("Cadastrar Serviço", use_container_width=True)
                if submitted_serv:
                    if not nome_serv or not cat_serv_sel:
                        st.error("Nome e Categoria são obrigatórios.")
                    else:
                        try:
                            sid = CadastroService.criar_servico(
                                categoria_id=dict_cat_serv[cat_serv_sel],
                                nome=nome_serv,
                                tipo_servico=tipo_serv,
                                preco_base=preco_base,
                                duracao_minutos=duracao,
                                comissao_padrao_pct=comissao_pct
                            )
                            st.success(f"Serviço cadastrado com sucesso! ID: {sid}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar serviço: {e}")

        with col_s_list:
            st.markdown("#### 🔍 Serviços Cadastrados")
            try:
                servicos = CadastroService.listar_servicos()
                if servicos:
                    df_serv = pd.DataFrame([
                        {
                            "ID": s["id"],
                            "Nome": s["nome"],
                            "Categoria": s["categoria_nome"],
                            "Tipo": s["tipo_servico"],
                            "Preço Base": f"R$ {float(s['preco_base']):.2f}",
                            "Duração": f"{s['duracao_minutos']} min",
                            "Comissão": f"{float(s['comissao_padrao_pct'] or 0):.1f}%"
                        }
                        for s in servicos
                    ])
                    st.dataframe(df_serv, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum serviço cadastrado.")
            except Exception as e:
                st.error(f"Erro ao carregar serviços: {e}")

    # =========================================================================
    # TAB 5: COLABORADORES
    # =========================================================================
    with tabs[4]:
        st.subheader("Equipe de Colaboradores & Vínculo Google Auth")
        st.caption("Cadastre médicos veterinários, tosadores e recepcionistas. Vincule o e-mail Google para controle de acesso.")
        col_c_list, col_c_form = st.columns([3, 2])

        with col_c_form:
            st.markdown("#### ➕ Novo Colaborador")
            with st.form("form_novo_colaborador", clear_on_submit=True):
                nome_colab = st.text_input("Nome Completo *")
                cpf_colab = st.text_input("CPF *", placeholder="000.000.000-00")
                tel_colab = st.text_input("Telefone *", placeholder="(87) 99999-0000")
                
                col_cg1, col_cg2 = st.columns(2)
                with col_cg1:
                    cargo = st.selectbox("Cargo *", ["VETERINARIO", "TOSADOR", "BANHISTA", "RECEPCIONISTA", "GERENTE"])
                    crmv = st.text_input("CRMV (se Veterinário)", placeholder="CRMV-PE 1234")
                with col_cg2:
                    comissao = st.number_input("Comissão Base (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
                    email_pessoal = st.text_input("E-mail Pessoal")

                auth_email = st.text_input("E-mail Google Auth (Supabase) *", placeholder="exemplo@gmail.com ou @ufape.edu.br", help="Permite ao sistema vincular a sessão do Google ao colaborador")

                submitted_colab = st.form_submit_button("Cadastrar Colaborador", use_container_width=True)
                if submitted_colab:
                    if not nome_colab or not cpf_colab or not tel_colab:
                        st.error("Nome, CPF e Telefone são obrigatórios.")
                    elif cargo == "VETERINARIO" and not crmv:
                        st.error("CRMV é obrigatório para o cargo de Veterinário.")
                    else:
                        try:
                            cid = CadastroService.criar_colaborador(
                                nome=nome_colab,
                                cpf=cpf_colab,
                                telefone=tel_colab,
                                cargo=cargo,
                                email=email_pessoal,
                                auth_email=auth_email,
                                crmv=crmv,
                                percentual_comissao=comissao
                            )
                            st.success(f"Colaborador cadastrado com sucesso! ID: {cid}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar colaborador: {e}")

        with col_c_list:
            st.markdown("#### 🔍 Colaboradores Ativos")
            try:
                colabs = CadastroService.listar_colaboradores()
                if colabs:
                    df_colabs = pd.DataFrame([
                        {
                            "ID": c["id"],
                            "Nome": c["nome"],
                            "Cargo": c["cargo"],
                            "CRMV": c["crmv"] or "-",
                            "Comissão": f"{float(c['percentual_comissao']):.1f}%",
                            "Google Auth": c["auth_email"] or "Sem vínculo",
                            "Telefone": c["telefone"]
                        }
                        for c in colabs
                    ])
                    st.dataframe(df_colabs, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum colaborador cadastrado.")
            except Exception as e:
                st.error(f"Erro ao carregar colaboradores: {e}")

    # =========================================================================
    # TAB 6: FORNECEDORES
    # =========================================================================
    with tabs[5]:
        st.subheader("Fornecedores de Produtos e Fármacos")
        col_f_list, col_f_form = st.columns([3, 2])

        with col_f_form:
            st.markdown("#### ➕ Novo Fornecedor")
            with st.form("form_novo_fornecedor", clear_on_submit=True):
                razao_social = st.text_input("Razão Social *")
                nome_fantasia = st.text_input("Nome Fantasia")
                cnpj = st.text_input("CNPJ *", placeholder="00.000.000/0001-00")
                tel_forn = st.text_input("Telefone *", placeholder="(81) 3333-0000")
                email_forn = st.text_input("E-mail Comercial")
                contato_nome = st.text_input("Nome do Vendedor / Representante")

                submitted_forn = st.form_submit_button("Cadastrar Fornecedor", use_container_width=True)
                if submitted_forn:
                    if not razao_social or not cnpj or not tel_forn:
                        st.error("Razão Social, CNPJ e Telefone são obrigatórios.")
                    else:
                        try:
                            fid = CadastroService.criar_fornecedor(
                                razao_social=razao_social,
                                nome_fantasia=nome_fantasia,
                                cnpj=cnpj,
                                telefone=tel_forn,
                                email=email_forn,
                                contato_nome=contato_nome
                            )
                            st.success(f"Fornecedor cadastrado com sucesso! ID: {fid}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar fornecedor: {e}")

        with col_f_list:
            st.markdown("#### 🔍 Fornecedores Ativos")
            try:
                fornecedores = CadastroService.listar_fornecedores()
                if fornecedores:
                    df_forn = pd.DataFrame([
                        {
                            "ID": f["id"],
                            "Nome Fantasia": f["nome_fantasia"],
                            "CNPJ": f["cnpj"],
                            "Contato": f["contato_nome"] or "-",
                            "Telefone": f["telefone"],
                            "E-mail": f["email"] or "-"
                        }
                        for f in fornecedores
                    ])
                    st.dataframe(df_forn, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum fornecedor cadastrado.")
            except Exception as e:
                st.error(f"Erro ao carregar fornecedores: {e}")

if __name__ == "__main__":
    render_cadastros_view()
