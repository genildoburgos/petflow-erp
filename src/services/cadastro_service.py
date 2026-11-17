from sqlalchemy import text
from src.database.connection import get_engine

class CadastroService:
    # -------------------------------------------------------------------------
    # ESPÉCIES E RAÇAS (HVU standard)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_especies():
        engine = get_engine()
        with engine.connect() as conn:
            query = text("SELECT id, nome, descricao FROM especies WHERE ativo = TRUE ORDER BY nome")
            return conn.execute(query).mappings().all()

    @staticmethod
    def listar_racas(especie_id: int | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT r.id, r.nome, r.porte, r.especie_id, e.nome AS especie_nome
                FROM racas r
                JOIN especies e ON r.especie_id = e.id
                WHERE r.ativo = TRUE
            """
            params = {}
            if especie_id:
                sql += " AND r.especie_id = :especie_id"
                params["especie_id"] = especie_id
            sql += " ORDER BY r.nome"
            return conn.execute(text(sql), params).mappings().all()

    # -------------------------------------------------------------------------
    # TUTORES (CLIENTES)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_tutores(termo_busca: str = ""):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT t.id, t.nome, t.cpf, t.telefone, t.email, t.observacoes,
                       e.rua, e.numero, e.bairro, e.cidade, e.cep
                FROM tutores t
                LEFT JOIN enderecos e ON t.endereco_id = e.id
                WHERE t.ativo = TRUE
            """
            params = {}
            if termo_busca:
                sql += " AND (LOWER(t.nome) LIKE :busca OR t.cpf LIKE :busca OR t.telefone LIKE :busca)"
                params["busca"] = f"%{termo_busca.lower()}%"
            sql += " ORDER BY t.nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def criar_tutor(
        nome: str,
        telefone: str,
        cpf: str = "",
        email: str = "",
        rg: str = "",
        observacoes: str = "",
        cep: str = "55292-000",
        rua: str = "",
        numero: str = "S/N",
        bairro: str = "Centro",
        cidade: str = "Garanhuns",
        uf: str = "PE"
    ) -> int:
        engine = get_engine()
        with engine.begin() as conn:
            endereco_id = None
            if rua:
                res_end = conn.execute(
                    text("""
                        INSERT INTO enderecos (cep, rua, numero, bairro, cidade, uf)
                        VALUES (:cep, :rua, :numero, :bairro, :cidade, :uf)
                        RETURNING id
                    """),
                    {"cep": cep, "rua": rua, "numero": numero, "bairro": bairro, "cidade": cidade, "uf": uf}
                )
                endereco_id = res_end.scalar_one()

            res_tutor = conn.execute(
                text("""
                    INSERT INTO tutores (endereco_id, nome, cpf, rg, telefone, email, observacoes)
                    VALUES (:endereco_id, :nome, :cpf, :rg, :telefone, :email, :observacoes)
                    RETURNING id
                """),
                {
                    "endereco_id": endereco_id,
                    "nome": nome.strip(),
                    "cpf": cpf.strip() if cpf else None,
                    "rg": rg.strip() if rg else None,
                    "telefone": telefone.strip(),
                    "email": email.strip() if email else None,
                    "observacoes": observacoes.strip() if observacoes else None
                }
            )
            return res_tutor.scalar_one()

    # -------------------------------------------------------------------------
    # ANIMAIS (PADRÃO HVU)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_animais(termo_busca: str = "", tutor_id: int | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT 
                    a.id, a.codigo_prontuario, a.nome, a.sexo, a.castrado, a.peso,
                    a.data_nascimento, a.alergias, a.obito,
                    t.id AS tutor_id, t.nome AS tutor_nome, t.telefone AS tutor_whatsapp,
                    r.id AS raca_id, r.nome AS raca_nome, r.porte,
                    e.nome AS especie_nome
                FROM animais a
                JOIN tutores t ON a.tutor_id = t.id
                JOIN racas r ON a.raca_id = r.id
                JOIN especies e ON r.especie_id = e.id
                WHERE a.ativo = TRUE
            """
            params = {}
            if tutor_id:
                sql += " AND a.tutor_id = :tutor_id"
                params["tutor_id"] = tutor_id
            if termo_busca:
                sql += " AND (LOWER(a.nome) LIKE :busca OR LOWER(a.codigo_prontuario) LIKE :busca OR LOWER(t.nome) LIKE :busca)"
                params["busca"] = f"%{termo_busca.lower()}%"
            sql += " ORDER BY a.nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def criar_animal(
        tutor_id: int,
        raca_id: int,
        nome: str,
        sexo: str,
        peso: float,
        castrado: bool = False,
        data_nascimento = None,
        alergias: str = "",
        foto_url: str = ""
    ) -> dict:
        engine = get_engine()
        with engine.begin() as conn:
            # Gerador de código de prontuário sequencial anual
            ano_atual = 2026
            res_seq = conn.execute(text("SELECT COUNT(*) + 1 FROM animais")).scalar_one()
            codigo_prontuario = f"PRONT-{ano_atual}-{res_seq:04d}"

            res_animal = conn.execute(
                text("""
                    INSERT INTO animais (
                        tutor_id, raca_id, codigo_prontuario, nome, sexo, castrado,
                        peso, data_nascimento, alergias, foto_url
                    ) VALUES (
                        :tutor_id, :raca_id, :codigo_prontuario, :nome, :sexo, :castrado,
                        :peso, :data_nascimento, :alergias, :foto_url
                    )
                    RETURNING id, codigo_prontuario
                """),
                {
                    "tutor_id": tutor_id,
                    "raca_id": raca_id,
                    "codigo_prontuario": codigo_prontuario,
                    "nome": nome.strip(),
                    "sexo": sexo,
                    "castrado": castrado,
                    "peso": float(peso),
                    "data_nascimento": data_nascimento,
                    "alergias": alergias.strip() if alergias else None,
                    "foto_url": foto_url.strip() if foto_url else None
                }
            )
            row = res_animal.mappings().one()
            return dict(row)

    # -------------------------------------------------------------------------
    # COLABORADORES (VETERINÁRIOS, TOSADORES, CAIXA, GERENTE)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_colaboradores(cargo: str | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT id, nome, cpf, telefone, email, auth_email, cargo, crmv, percentual_comissao, ativo
                FROM colaboradores
                WHERE ativo = TRUE
            """
            params = {}
            if cargo:
                sql += " AND cargo = :cargo"
                params["cargo"] = cargo
            sql += " ORDER BY nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def criar_colaborador(
        nome: str,
        cpf: str,
        telefone: str,
        cargo: str,
        email: str = "",
        auth_email: str = "",
        crmv: str = "",
        percentual_comissao: float = 0.0
    ) -> int:
        engine = get_engine()
        with engine.begin() as conn:
            res = conn.execute(
                text("""
                    INSERT INTO colaboradores (
                        nome, cpf, telefone, email, auth_email, cargo, crmv, percentual_comissao
                    ) VALUES (
                        :nome, :cpf, :telefone, :email, :auth_email, :cargo, :crmv, :percentual_comissao
                    ) RETURNING id
                """),
                {
                    "nome": nome.strip(),
                    "cpf": cpf.strip(),
                    "telefone": telefone.strip(),
                    "email": email.strip() if email else None,
                    "auth_email": auth_email.strip() if auth_email else None,
                    "cargo": cargo,
                    "crmv": crmv.strip() if crmv else None,
                    "percentual_comissao": float(percentual_comissao)
                }
            )
            return res.scalar_one()

    # -------------------------------------------------------------------------
    # FORNECEDORES
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_fornecedores():
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT f.id, f.razao_social, f.nome_fantasia, f.cnpj, f.telefone, f.email, f.contato_nome,
                       e.rua, e.numero, e.bairro, e.cidade
                FROM fornecedores f
                LEFT JOIN enderecos e ON f.endereco_id = e.id
                WHERE f.ativo = TRUE
                ORDER BY f.nome_fantasia ASC
            """)
            return conn.execute(query).mappings().all()

    @staticmethod
    def criar_fornecedor(
        razao_social: str,
        nome_fantasia: str,
        cnpj: str,
        telefone: str,
        email: str = "",
        contato_nome: str = ""
    ) -> int:
        engine = get_engine()
        with engine.begin() as conn:
            res = conn.execute(
                text("""
                    INSERT INTO fornecedores (razao_social, nome_fantasia, cnpj, telefone, email, contato_nome)
                    VALUES (:razao_social, :nome_fantasia, :cnpj, :telefone, :email, :contato_nome)
                    RETURNING id
                """),
                {
                    "razao_social": razao_social.strip(),
                    "nome_fantasia": nome_fantasia.strip() or razao_social.strip(),
                    "cnpj": cnpj.strip(),
                    "telefone": telefone.strip(),
                    "email": email.strip() if email else None,
                    "contato_nome": contato_nome.strip() if contato_nome else None
                }
            )
            return res.scalar_one()

    # -------------------------------------------------------------------------
    # CATEGORIAS
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_categorias(tipo: str | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = "SELECT id, nome, tipo FROM categorias WHERE ativo = TRUE"
            params = {}
            if tipo:
                sql += " AND tipo = :tipo"
                params["tipo"] = tipo
            sql += " ORDER BY nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    # -------------------------------------------------------------------------
    # PRODUTOS (REVENDA & INSUMOS)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_produtos(apenas_revenda: bool = False, categoria_id: int | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT 
                    p.id, p.nome, p.codigo_barras, p.tipo_produto, p.unidade_medida,
                    p.preco_custo, p.preco_venda, p.estoque_minimo, p.estoque_atual,
                    c.nome AS categoria_nome,
                    (p.estoque_atual <= p.estoque_minimo) AS estoque_critico
                FROM produtos p
                JOIN categorias c ON p.categoria_id = c.id
                WHERE p.ativo = TRUE
            """
            params = {}
            if apenas_revenda:
                sql += " AND p.tipo_produto IN ('REVENDA', 'AMBOS')"
            if categoria_id:
                sql += " AND p.categoria_id = :categoria_id"
                params["categoria_id"] = categoria_id
            sql += " ORDER BY p.nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def criar_produto(
        categoria_id: int,
        nome: str,
        tipo_produto: str,
        unidade_medida: str,
        preco_custo: float,
        preco_venda: float,
        estoque_minimo: float = 5.0,
        estoque_inicial: float = 0.0,
        codigo_barras: str = ""
    ) -> int:
        engine = get_engine()
        with engine.begin() as conn:
            res = conn.execute(
                text("""
                    INSERT INTO produtos (
                        categoria_id, codigo_barras, nome, tipo_produto, unidade_medida,
                        preco_custo, preco_venda, estoque_minimo, estoque_atual
                    ) VALUES (
                        :categoria_id, :codigo_barras, :nome, :tipo_produto, :unidade_medida,
                        :preco_custo, :preco_venda, :estoque_minimo, :estoque_inicial
                    ) RETURNING id
                """),
                {
                    "categoria_id": categoria_id,
                    "codigo_barras": codigo_barras.strip() if codigo_barras else None,
                    "nome": nome.strip(),
                    "tipo_produto": tipo_produto,
                    "unidade_medida": unidade_medida,
                    "preco_custo": float(preco_custo),
                    "preco_venda": float(preco_venda),
                    "estoque_minimo": float(estoque_minimo),
                    "estoque_atual": float(estoque_inicial)
                }
            )
            prod_id = res.scalar_one()

            if estoque_inicial > 0:
                conn.execute(
                    text("""
                        INSERT INTO movimentacoes_estoque (
                            produto_id, tipo_movimento, quantidade,
                            estoque_anterior, estoque_posterior,
                            origem_modulo, origem_id, justificativa
                        ) VALUES (
                            :produto_id, 'AJUSTE_INVENTARIO', :quantidade,
                            0, :quantidade, 'INVENTARIO', :prod_id, 'Saldo Inicial de Cadastro'
                        )
                    """),
                    {"produto_id": prod_id, "quantidade": float(estoque_inicial), "prod_id": prod_id}
                )

            return prod_id

    # -------------------------------------------------------------------------
    # SERVIÇOS (ESTÉTICA E CLÍNICO)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_servicos(tipo_servico: str | None = None):
        engine = get_engine()
        with engine.connect() as conn:
            sql = """
                SELECT s.id, s.nome, s.tipo_servico, s.preco_base, s.duracao_minutos,
                       s.comissao_padrao_pct, c.nome AS categoria_nome
                FROM servicos s
                JOIN categorias c ON s.categoria_id = c.id
                WHERE s.ativo = TRUE
            """
            params = {}
            if tipo_servico:
                sql += " AND s.tipo_servico = :tipo_servico"
                params["tipo_servico"] = tipo_servico
            sql += " ORDER BY s.nome ASC"
            return conn.execute(text(sql), params).mappings().all()

    @staticmethod
    def criar_servico(
        categoria_id: int,
        nome: str,
        tipo_servico: str,
        preco_base: float,
        duracao_minutos: int = 60,
        comissao_padrao_pct: float | None = None
    ) -> int:
        engine = get_engine()
        with engine.begin() as conn:
            res = conn.execute(
                text("""
                    INSERT INTO servicos (
                        categoria_id, nome, tipo_servico, preco_base, duracao_minutos, comissao_padrao_pct
                    ) VALUES (
                        :categoria_id, :nome, :tipo_servico, :preco_base, :duracao_minutos, :comissao_padrao_pct
                    ) RETURNING id
                """),
                {
                    "categoria_id": categoria_id,
                    "nome": nome.strip(),
                    "tipo_servico": tipo_servico,
                    "preco_base": float(preco_base),
                    "duracao_minutos": int(duracao_minutos),
                    "comissao_padrao_pct": float(comissao_padrao_pct) if comissao_padrao_pct is not None else None
                }
            )
            return res.scalar_one()

    # -------------------------------------------------------------------------
    # MEDICAMENTOS (CATÁLOGO HVU)
    # -------------------------------------------------------------------------
    @staticmethod
    def listar_medicamentos():
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT m.id, m.nome, m.principio_ativo, m.concentracao, m.via_administracao, m.detalhes,
                       p.estoque_atual, p.preco_venda
                FROM medicamentos m
                LEFT JOIN produtos p ON m.produto_id = p.id
                WHERE m.ativo = TRUE
                ORDER BY m.nome ASC
            """)
            return conn.execute(query).mappings().all()
