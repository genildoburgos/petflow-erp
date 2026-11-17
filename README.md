# 🐾 PetFlow ERP — Sistema Integrado de Gestão Pet & Vet

> **Projeto Prático da Disciplina:** Sistemas de Informação e Tecnologias (2026.2)  
> **Instituição:** Universidade Federal do Agreste de Pernambuco (UFAPE) — Bacharelado em Ciência da Computação  
> **Docente:** Prof. Dr. Assuero Fonseca Ximenes  
> **Discente:** Genildo Burgos  

---

## 📌 1. Visão Geral do Projeto

O **PetFlow ERP** é uma solução de ERP vertical simplificada e moderna desenvolvida especificamente para o segmento de **Pet Shops e Clínicas Veterinárias**. 

O sistema foi concebido a partir de:
1. **Pesquisa de Mercado:** Benchmark aprofundado dos principais players nacionais (*SimplesVet, Vetus, Nuvem Vet e Sispet*).
2. **Simulação Multiagente (Mirofish):** Análise sintética de 25 personas (médicos veterinários, tosadores, atendentes e tutores) para identificar dores críticas reais (reclamações de quebra de estoque, lentidão no checkout e litígios por lesões prévias).
3. **Padrão de Domínio HVU:** Alinhamento técnico com a arquitetura relacional e clínica do **Hospital Veterinário Universitário (HVU / LMTS da UFAPE)**, adotando prontuário estruturado (anamnese, avaliação física geral e prescrições digitais).

---

## 🏗️ 2. Arquitetura & Stack Tecnológica

- **Linguagem & Interface:** Python 3.12 + [Streamlit](https://streamlit.io/) (Navegação moderna com `st.navigation` e `st.Page`).
- **Banco de Dados Relacional:** [PostgreSQL](https://www.postgresql.org/) hospedado na nuvem via [Supabase](https://supabase.com/).
- **Camada de Acesso a Dados & ORM:** SQLAlchemy 2.0 com dialetos `psycopg` e `psycopg2`.
- **Autenticação & Auditoria:** Integração nativa com Google Auth (Supabase Auth / Streamlit Auth) mapeada para a tabela `colaboradores` via coluna `auth_email`.
- **Orquestração Transacional ("Efeito Dominó"):** Operações integradas entre compras/vendas/atendimentos e estoque/financeiro executadas com atomicidade (`BEGIN ... COMMIT / ROLLBACK`) e trava em nível de linha (`SELECT FOR UPDATE`).

---

## 🧩 3. Módulos Implementados (1ª VA — Foco Transacional OLTP)

| Módulo | Descrição & Funcionalidades |
| :--- | :--- |
| **🏠 Painel Operacional** | Visão geral da operação diária, fila do dia no banho/tosa, consultas médicas recentes e alertas de estoque crítico. |
| **⚡ Atendimento Operacional** | **Estética:** Check-in visual de segurança (inspeção de nós, pulgas e ferimentos), pipeline de status e aviso dinâmico no WhatsApp em 1 clique.<br>**Clínico (Padrão HVU):** Prontuário médico com anamnese, avaliação físico-geral (temperatura, FC, FR, TPC), receituário e baixa automática de vacinas no estoque. |
| **🛒 Frente de Caixa (Fast-POS)** | Checkout em tela única: faturamento unificado de ordens de serviço de estética, consultas clínicas e produtos de varejo com baixa atômica de estoque e geração de receita. |
| **📥 Compras & Entrada NF** | Registro de notas fiscais de fornecedores com efeito dominó: incremento de estoque, log de auditoria e lançamento automático no contas a pagar. |
| **📦 Estoque & Rastreabilidade** | Posição física e valorização de insumos e revenda, controle de estoque mínimo com alertas visuais, ajuste de inventário e log imutável de movimentações. |
| **💰 Financeiro & Caixa** | Fluxo de caixa com saldo realizado e projetado, extrato de títulos, baixa rápida de contas a pagar/receber e lançamento manual de custos fixos. |
| **🗂️ Cadastros Mestres** | CRUD completo de Animais (com Prontuário sequencial), Tutores (com Endereço normalizado), Produtos, Serviços, Colaboradores (com CRMV e comissões) e Fornecedores. |

---

## 🚀 4. Como Executar o Projeto Localmente

### Pré-requisitos:
- Python 3.12+ instalado.
- Conta e projeto configurado no PostgreSQL / Supabase.

### Passo a Passo:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/genildoburgos/petflow-erp.git
   cd petflow-erp
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Linux/Mac
   # ou .venv\Scripts\activate no Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais do banco:**
   Crie o arquivo `.streamlit/secrets.toml` baseado no template `.streamlit/secrets.toml.example`:
   ```toml
   [database]
   url = "postgresql://postgres.SEU_PROJETO:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

   [auth]
   admin_email = "professor@ufape.edu.br"
   ```

5. **Execute a aplicação Streamlit:**
   ```bash
   streamlit run app.py
   ```
   Acesse no navegador: `http://localhost:8501`.

---

## 📁 5. Estrutura do Repositório

```text
petflow-erp/
├── .streamlit/
│   ├── config.toml               # Tema customizado (Teal / Slate)
│   └── secrets.toml.example      # Template de credenciais de produção
├── docs/
│   ├── 01_pesquisa_mercado_concorrentes.md
│   ├── 02_analise_mirofish_simulacao.md
│   ├── 03_especificacao_projeto_ufape.md
│   ├── 04_comparativo_e_decisoes_hvu.md
│   ├── 04_modelo_dados_postgre_sql.sql     # DDL oficial do PostgreSQL
│   └── 05_seed_dados_iniciais.sql          # Carga de dados iniciais
├── src/
│   ├── auth/
│   │   └── auth_manager.py       # Vínculo Google Auth / Supabase Auth
│   ├── database/
│   │   └── connection.py         # SQLAlchemy Engine & Pool de conexões
│   ├── services/
│   │   ├── atendimento_service.py # Lógica de Estética e Clínica (HVU)
│   │   ├── cadastro_service.py    # CRUD de entidades mestres
│   │   ├── compra_service.py      # Efeito dominó de Compras
│   │   ├── estoque_service.py     # Posição, Alertas e Inventário
│   │   ├── financeiro_service.py  # Fluxo de caixa e Conciliação
│   │   └── venda_service.py       # Efeito dominó de Vendas (Fast POS)
│   └── views/
│       ├── cadastros_view.py      # Tela de Cadastros Mestres
│       ├── compras_view.py        # Tela de Entrada de Compras
│       ├── estoque_view.py        # Tela de Estoque & Movimentações
│       ├── financeiro_view.py     # Tela de Finanças & Títulos
│       ├── home.py                # Dashboard Operacional
│       ├── operacional_view.py    # Tela de Banho/Tosa & Consultório
│       └── pdv_view.py            # Tela de Frente de Caixa Unificada
├── app.py                         # Ponto de entrada (st.navigation)
├── requirements.txt               # Dependências Python
└── README.md                      # Documentação técnica do projeto
```

---

## 📄 Licença & Finalidade

Desenvolvido exclusivamente para fins acadêmicos como parte da avaliação da disciplina **Sistemas de Informação e Tecnologias (2026.2)** da UFAPE.
