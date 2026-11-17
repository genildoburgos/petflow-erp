-- ==============================================================================
-- PROJETO PRÁTICO: SISTEMAS DE INFORMAÇÃO E TECNOLOGIAS (UFAPE 2026.2)
-- PROFESSOR: DR. ASSUERO FONSECA XIMENES
-- SISTEMA: PetFlow ERP - Gestão Integrada para Pet Shops e Clínicas Veterinárias
-- ARQUITETURA DE DADOS: PostgreSQL (Supabase)
-- NOTA TÉCNICA: Modelo relacional construído cruzando os requisitos de ERP (compras,
-- vendas, estoque, financeiro) com o modelo de domínio clínico real do HVU/UFAPE
-- (Hospital Veterinário Universitário - LMTS).
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 0. EXTENSÕES & CONFIGURAÇÕES GERAIS
-- ------------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. MÓDULO CADASTROS MESTRES (BASE ESTRUTURAL & MODELO HVU)
-- ------------------------------------------------------------------------------

-- 1.1 Tabela de Endereços Normalizada (Inspirada no modelo HVU)
CREATE TABLE IF NOT EXISTS enderecos (
    id SERIAL PRIMARY KEY,
    cep VARCHAR(10) NOT NULL,
    rua VARCHAR(150) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    complemento VARCHAR(100),
    bairro VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL DEFAULT 'Garanhuns',
    uf CHAR(2) NOT NULL DEFAULT 'PE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 Espécies (Inspirado no modelo HVU)
CREATE TABLE IF NOT EXISTS especies (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(60) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 Raças (Inspirado no modelo HVU: associado a Especie e com Porte)
CREATE TABLE IF NOT EXISTS racas (
    id SERIAL PRIMARY KEY,
    especie_id INTEGER NOT NULL REFERENCES especies(id) ON DELETE RESTRICT,
    nome VARCHAR(80) NOT NULL,
    porte VARCHAR(20) NOT NULL DEFAULT 'Médio' CHECK (porte IN ('Mini', 'Pequeno', 'Médio', 'Grande', 'Gigante')),
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unq_raca_especie UNIQUE (especie_id, nome)
);

-- 1.4 Tutores / Clientes (Herança conceitual de Usuário/Endereço do HVU)
CREATE TABLE IF NOT EXISTS tutores (
    id SERIAL PRIMARY KEY,
    endereco_id INTEGER REFERENCES enderecos(id) ON DELETE SET NULL,
    nome VARCHAR(150) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    rg VARCHAR(20),
    telefone VARCHAR(20) NOT NULL, -- WhatsApp para notificações e avisos
    email VARCHAR(120),
    observacoes TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.5 Animais (Atributos clínicos enriquecidos com padrão HVU)
CREATE TABLE IF NOT EXISTS animais (
    id SERIAL PRIMARY KEY,
    tutor_id INTEGER NOT NULL REFERENCES tutores(id) ON DELETE RESTRICT,
    raca_id INTEGER NOT NULL REFERENCES racas(id) ON DELETE RESTRICT,
    codigo_prontuario VARCHAR(30) UNIQUE NOT NULL, -- Ex: PRONT-2026-0001
    nome VARCHAR(100) NOT NULL,
    sexo CHAR(1) NOT NULL CHECK (sexo IN ('M', 'F')),
    castrado BOOLEAN NOT NULL DEFAULT FALSE,
    peso NUMERIC(5,2) NOT NULL CHECK (peso > 0), -- em kg
    data_nascimento DATE,
    alergias TEXT,
    foto_url TEXT,
    obito BOOLEAN NOT NULL DEFAULT FALSE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.6 Colaboradores (Médicos Veterinários com CRMV, Tosadores com Comissão, Recepcionistas)
CREATE TABLE IF NOT EXISTS colaboradores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(120),
    auth_email VARCHAR(120) UNIQUE, -- Vínculo com o e-mail da conta Google autenticada (Supabase / Streamlit Auth)
    cargo VARCHAR(40) NOT NULL CHECK (cargo IN ('VETERINARIO', 'TOSADOR', 'BANHISTA', 'RECEPCIONISTA', 'GERENTE')),
    crmv VARCHAR(20), -- Obrigatório para VETERINARIO
    percentual_comissao NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (percentual_comissao >= 0 AND percentual_comissao <= 100),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.7 Fornecedores (Empresas distribuidoras de rações, insumos e fármacos)
CREATE TABLE IF NOT EXISTS fornecedores (
    id SERIAL PRIMARY KEY,
    endereco_id INTEGER REFERENCES enderecos(id) ON DELETE SET NULL,
    razao_social VARCHAR(150) NOT NULL,
    nome_fantasia VARCHAR(150),
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(120),
    contato_nome VARCHAR(100),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.8 Categorias de Itens (Classificação de Produtos e Serviços)
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('PRODUTO', 'SERVICO')),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.9 Serviços (Estética, Banho, Tosa, Consultas, Procedimentos)
CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    nome VARCHAR(120) NOT NULL,
    tipo_servico VARCHAR(20) NOT NULL CHECK (tipo_servico IN ('ESTETICA', 'CLINICO')),
    preco_base NUMERIC(10,2) NOT NULL CHECK (preco_base >= 0),
    duracao_minutos INTEGER NOT NULL DEFAULT 60,
    comissao_padrao_pct NUMERIC(5,2) DEFAULT NULL, -- Se nulo, adota a comissão do colaborador
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.10 Produtos (Revenda e Insumos Operacionais)
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    codigo_barras VARCHAR(50) UNIQUE,
    nome VARCHAR(150) NOT NULL,
    tipo_produto VARCHAR(25) NOT NULL CHECK (tipo_produto IN ('REVENDA', 'INSUMO_OPERACIONAL', 'AMBOS')),
    unidade_medida VARCHAR(10) NOT NULL DEFAULT 'UN' CHECK (unidade_medida IN ('UN', 'KG', 'L', 'ML', 'DOSE', 'PCT')),
    preco_custo NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (preco_custo >= 0),
    preco_venda NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (preco_venda >= 0),
    estoque_minimo NUMERIC(10,2) NOT NULL DEFAULT 5.00,
    estoque_atual NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1.11 Medicamentos (Catálogo de Fármacos para Receituário - Base HVU)
CREATE TABLE IF NOT EXISTS medicamentos (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER REFERENCES produtos(id) ON DELETE SET NULL, -- Vínculo opcional se o remédio estiver em estoque na clínica
    nome VARCHAR(150) NOT NULL,
    principio_ativo VARCHAR(150),
    concentracao VARCHAR(60), -- Ex: '50mg', '10mg/ml'
    via_administracao VARCHAR(50) DEFAULT 'Oral', -- Oral, Tópica, Injetável, Otológica
    detalhes TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 2. MÓDULO COMPRAS & ENTRADA DE NOTAS (INTEGRADO A ESTOQUE E FINANCEIRO)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS compras (
    id SERIAL PRIMARY KEY,
    fornecedor_id INTEGER NOT NULL REFERENCES fornecedores(id) ON DELETE RESTRICT,
    numero_nota VARCHAR(50),
    data_compra DATE NOT NULL DEFAULT CURRENT_DATE,
    valor_total NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (valor_total >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'RECEBIDO' CHECK (status IN ('PENDENTE', 'RECEBIDO', 'CANCELADO')),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_compra (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade NUMERIC(10,2) NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL CHECK (preco_unitario >= 0),
    subtotal NUMERIC(10,2) GENERATED ALWAYS AS (quantidade * preco_unitario) STORED
);

-- ------------------------------------------------------------------------------
-- 3. MÓDULO AGENDAMENTO & VAGAS (INSPIRADO NO FLUXO HVU)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE RESTRICT,
    colaborador_id INTEGER NOT NULL REFERENCES colaboradores(id) ON DELETE RESTRICT,
    servico_id INTEGER NOT NULL REFERENCES servicos(id) ON DELETE RESTRICT,
    data_horario TIMESTAMP WITH TIME ZONE NOT NULL,
    tipo_especial BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(25) NOT NULL DEFAULT 'AGENDADO' 
        CHECK (status IN ('AGENDADO', 'CONFIRMADO', 'EM_ATENDIMENTO', 'CONCLUIDO', 'CANCELADO')),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cancelamentos (
    id SERIAL PRIMARY KEY,
    agendamento_id INTEGER NOT NULL REFERENCES agendamentos(id) ON DELETE CASCADE,
    data_cancelamento TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 4. MÓDULO OPERACIONAL: ATENDIMENTO CLÍNICO (PRONTUÁRIO COMPLETO HVU)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS consultas_veterinarias (
    id SERIAL PRIMARY KEY,
    numero_consulta VARCHAR(30) UNIQUE NOT NULL, -- Ex: CONS-202611-0001
    agendamento_id INTEGER REFERENCES agendamentos(id) ON DELETE SET NULL,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE RESTRICT,
    veterinario_id INTEGER NOT NULL REFERENCES colaboradores(id) ON DELETE RESTRICT,
    
    data_consulta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    peso_atual NUMERIC(5,2) NOT NULL CHECK (peso_atual > 0),
    idade_atual_meses INTEGER,
    tipo_consulta VARCHAR(20) NOT NULL DEFAULT 'PRIMEIRA_VEZ' CHECK (tipo_consulta IN ('PRIMEIRA_VEZ', 'RETORNO')),
    
    -- Anamnese clínica (Estrutura HVU)
    queixa_principal TEXT NOT NULL,
    alteracoes_clinicas_diversas TEXT,
    suspeitas_clinicas TEXT,
    alimentacao VARCHAR(150),
    
    -- Exame físico geral e sinais vitais (HVU AvaliacaoFisicoGeral)
    temperatura_celsius NUMERIC(4,1), -- Ex: 38.5
    frequencia_cardiaca_bpm INTEGER,  -- Ex: 110
    frequencia_respiratoria_mpm INTEGER, -- Ex: 24
    tpc_segundos INTEGER, -- Tempo de Preenchimento Capilar (1 a 2s normal)
    nivel_consciencia VARCHAR(50) DEFAULT 'Alerta', -- Alerta, Deprimido, Comatoso
    nivel_hidratacao VARCHAR(50) DEFAULT 'Normal',  -- Normal, Desidratação Leve, Moderada, Grave
    tipo_mucosa VARCHAR(50) DEFAULT 'Normocorada',  -- Normocorada, Pálida, Congesta, Ictérica
    
    -- Parecer e conduta
    parecer_diagnostico TEXT,
    proxima_consulta_recomendada DATE,
    
    -- Valores comerciais e comissão
    valor_consulta NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (valor_consulta >= 0),
    percentual_comissao NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    valor_comissao NUMERIC(10,2) GENERATED ALWAYS AS (valor_consulta * (percentual_comissao / 100.0)) STORED,
    
    status VARCHAR(20) NOT NULL DEFAULT 'FINALIZADA' CHECK (status IN ('EM_ANDAMENTO', 'FINALIZADA', 'CANCELADA')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Prescrições médicas associadas à consulta (Receituário digital HVU)
CREATE TABLE IF NOT EXISTS prescricoes (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES consultas_veterinarias(id) ON DELETE CASCADE,
    medicamento_id INTEGER NOT NULL REFERENCES medicamentos(id) ON DELETE RESTRICT,
    dose VARCHAR(80) NOT NULL, -- Ex: '1 comprimido', '2.5 ml'
    frequencia VARCHAR(80) NOT NULL, -- Ex: 'A cada 12 horas', 'Uma vez ao dia'
    periodo_dias INTEGER NOT NULL, -- Ex: 7 dias
    observacoes_administracao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insumos consumidos na consulta (Vacinas aplicadas, seringas, medicamentos de estoque)
CREATE TABLE IF NOT EXISTS insumos_consulta (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES consultas_veterinarias(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade_utilizada NUMERIC(10,2) NOT NULL CHECK (quantidade_utilizada > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 5. MÓDULO OPERACIONAL: ATENDIMENTO DE ESTÉTICA (BANHO, TOSA & CHECK-IN VISUAL)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS atendimentos_estetica (
    id SERIAL PRIMARY KEY,
    numero_os VARCHAR(30) UNIQUE NOT NULL, -- Ex: OS-202611-0001
    agendamento_id INTEGER REFERENCES agendamentos(id) ON DELETE SET NULL,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE RESTRICT,
    servico_id INTEGER NOT NULL REFERENCES servicos(id) ON DELETE RESTRICT,
    colaborador_id INTEGER NOT NULL REFERENCES colaboradores(id) ON DELETE RESTRICT, -- Tosador/Banhista
    
    -- Esteira operacional visual
    status VARCHAR(25) NOT NULL DEFAULT 'RECEBIDO_CHECKIN' 
        CHECK (status IN ('AGENDADO', 'RECEBIDO_CHECKIN', 'EM_BANHO', 'EM_TOSA', 'PRONTO_AVISAR', 'FINALIZADO_ENTREGUE', 'CANCELADO')),
    
    data_hora_entrada TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_hora_conclusao TIMESTAMP WITH TIME ZONE,
    
    -- Check-in de segurança visual (Mitigação de litígios - Dores de mercado)
    tem_pulgas BOOLEAN NOT NULL DEFAULT FALSE,
    tem_nos_pelagem BOOLEAN NOT NULL DEFAULT FALSE,
    tem_ferimento_previo BOOLEAN NOT NULL DEFAULT FALSE,
    foto_checkin_url TEXT,
    observacoes_manejo TEXT,
    
    -- Valores comerciais e comissionamento
    valor_servico NUMERIC(10,2) NOT NULL CHECK (valor_servico >= 0),
    percentual_comissao NUMERIC(5,2) NOT NULL CHECK (percentual_comissao >= 0),
    valor_comissao NUMERIC(10,2) GENERATED ALWAYS AS (valor_servico * (percentual_comissao / 100.0)) STORED,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insumos consumidos na estética (Shampoos, condicionadores, perfumes)
CREATE TABLE IF NOT EXISTS insumos_estetica (
    id SERIAL PRIMARY KEY,
    atendimento_estetica_id INTEGER NOT NULL REFERENCES atendimentos_estetica(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade_utilizada NUMERIC(10,2) NOT NULL CHECK (quantidade_utilizada > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 6. MÓDULO VENDAS & FRENTE DE CAIXA (FAST-POS EM 1 TELA)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS vendas (
    id SERIAL PRIMARY KEY,
    numero_venda VARCHAR(30) UNIQUE NOT NULL, -- Ex: VENDA-202611-0001
    tutor_id INTEGER REFERENCES tutores(id) ON DELETE SET NULL,
    consulta_id INTEGER REFERENCES consultas_veterinarias(id) ON DELETE SET NULL, -- Se faturando consulta médica
    atendimento_estetica_id INTEGER REFERENCES atendimentos_estetica(id) ON DELETE SET NULL, -- Se faturando banho/tosa
    colaborador_caixa_id INTEGER NOT NULL REFERENCES colaboradores(id) ON DELETE RESTRICT,
    
    data_venda TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    subtotal NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (subtotal >= 0),
    desconto NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (desconto >= 0),
    valor_total NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (valor_total >= 0),
    
    forma_pagamento VARCHAR(25) NOT NULL CHECK (forma_pagamento IN ('PIX', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'DINHEIRO', 'FIADO_PARCELADO')),
    status VARCHAR(20) NOT NULL DEFAULT 'FINALIZADA' CHECK (status IN ('FINALIZADA', 'CANCELADA')),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES vendas(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade NUMERIC(10,2) NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL CHECK (preco_unitario >= 0),
    subtotal NUMERIC(10,2) GENERATED ALWAYS AS (quantidade * preco_unitario) STORED
);

-- ------------------------------------------------------------------------------
-- 7. MÓDULO ESTOQUE (LOG TRANSACIONAL & RASTREABILIDADE TEMPORAL)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    tipo_movimento VARCHAR(35) NOT NULL CHECK (tipo_movimento IN (
        'ENTRADA_COMPRA', 'SAIDA_VENDA_PDV', 'SAIDA_CONSUMO_ESTETICA', 
        'SAIDA_CONSUMO_CLINICA', 'AJUSTE_INVENTARIO', 'CANCELAMENTO'
    )),
    quantidade NUMERIC(10,2) NOT NULL, -- Positivo (entrada) ou Negativo (saída)
    estoque_anterior NUMERIC(10,2) NOT NULL,
    estoque_posterior NUMERIC(10,2) NOT NULL,
    
    origem_modulo VARCHAR(20) NOT NULL CHECK (origem_modulo IN ('COMPRAS', 'VENDAS', 'ESTETICA', 'CLINICA', 'INVENTARIO')),
    origem_id INTEGER, -- ID da compra, venda, atendimento_estetica ou consulta
    
    justificativa TEXT,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 8. MÓDULO FINANCEIRO (FLUXO DE CAIXA, CONTAS A PAGAR & RECEBER)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financeiro_lancamentos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('RECEITA', 'DESPESA')),
    categoria_financeira VARCHAR(50) NOT NULL CHECK (categoria_financeira IN (
        'VENDA_BALCAO', 'SERVICO_ESTETICA', 'CONSULTA_CLINICA', 
        'COMPRA_FORNECEDOR', 'COMISSAO_COLABORADOR', 'CUSTO_FIXO', 'OUTROS'
    )),
    descricao VARCHAR(200) NOT NULL,
    valor NUMERIC(10,2) NOT NULL CHECK (valor > 0),
    
    data_competencia DATE NOT NULL DEFAULT CURRENT_DATE,
    data_vencimento DATE NOT NULL DEFAULT CURRENT_DATE,
    data_pagamento DATE,
    
    status VARCHAR(20) NOT NULL DEFAULT 'PAGO' CHECK (status IN ('PENDENTE', 'PAGO', 'CANCELADO')),
    forma_pagamento VARCHAR(25) CHECK (forma_pagamento IN ('PIX', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'DINHEIRO', 'BOLETO')),
    
    origem_modulo VARCHAR(20) NOT NULL CHECK (origem_modulo IN ('VENDAS', 'COMPRAS', 'ESTETICA', 'CLINICA', 'MANUAL')),
    origem_id INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 9. ÍNDICES DE PERFORMANCE E INTEGRIDADE
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_racas_especie ON racas(especie_id);
CREATE INDEX IF NOT EXISTS idx_animais_tutor ON animais(tutor_id);
CREATE INDEX IF NOT EXISTS idx_animais_raca ON animais(raca_id);
CREATE INDEX IF NOT EXISTS idx_animais_prontuario ON animais(codigo_prontuario);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_horario);
CREATE INDEX IF NOT EXISTS idx_consultas_animal ON consultas_veterinarias(animal_id);
CREATE INDEX IF NOT EXISTS idx_consultas_vet ON consultas_veterinarias(veterinario_id);
CREATE INDEX IF NOT EXISTS idx_estetica_animal ON atendimentos_estetica(animal_id);
CREATE INDEX IF NOT EXISTS idx_estetica_colaborador ON atendimentos_estetica(colaborador_id);
CREATE INDEX IF NOT EXISTS idx_estetica_status ON atendimentos_estetica(status);
CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda);
CREATE INDEX IF NOT EXISTS idx_mov_estoque_produto ON movimentacoes_estoque(produto_id);
CREATE INDEX IF NOT EXISTS idx_mov_estoque_data ON movimentacoes_estoque(data_hora);
CREATE INDEX IF NOT EXISTS idx_financeiro_competencia ON financeiro_lancamentos(data_competencia);

-- ------------------------------------------------------------------------------
