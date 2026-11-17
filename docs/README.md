# Base de Conhecimento & Documentação do Projeto: PetFlow ERP

Bem-vindo à pasta `docs/` do projeto **PetFlow ERP**, concebido como projeto prático da disciplina de **Sistemas de Informação e Tecnologias** (UFAPE 2026.2) e direcionado para resolver as dores reais do mercado brasileiro de pet shops e clínicas veterinárias.

---

## Estrutura dos Documentos

| Arquivo | Descrição |
| :--- | :--- |
| **[`01_pesquisa_mercado_concorrentes.md`](./01_pesquisa_mercado_concorrentes.md)** | Benchmarking aprofundado dos líderes (SimplesVet, Vetus, Nuvem Vet, Sispet), mapeamento dos 5 grandes gargalos da indústria e proposta de valor do "ERP Simplificado". |
| **[`02_analise_mirofish_simulacao.md`](./02_analise_mirofish_simulacao.md)** | Síntese da simulação social no MiroFish (25 personas, 80+ posts/comentários), mapeamento de gambiarras do setor e matriz *Kill vs. Keep* para o MVP. |
| **[`03_especificacao_projeto_ufape.md`](./03_especificacao_projeto_ufape.md)** | Requisitos acadêmicos do Prof. Dr. Assuero Ximenes (UFAPE), detalhamento dos 6 módulos obrigatórios integrados, stack técnica (Python/Streamlit/Supabase/Google Auth) e preparação para a 2ª VA (BI). |
| **[`04_modelo_dados_postgre_sql.sql`](./04_modelo_dados_postgre_sql.sql)** | Script DDL transacional para PostgreSQL/Supabase com 14 tabelas relacionais, integridade referencial, foreign keys, índices e vínculo com Google Auth (`auth_email`). |
| **[`05_seed_dados_iniciais.sql`](./05_seed_dados_iniciais.sql)** | Carga inicial de dados realistas (Categorias, Serviços de banho/clínica, Produtos de revenda e insumos, Fornecedores, Tutores e Pets). |
| **[`seed_pesquisa_04_erp_pet_veterinaria.txt`](./seed_pesquisa_04_erp_pet_veterinaria.txt)** | Cópia de segurança do prompt/seed original utilizado no motor de simulação multi-agente MiroFish. |

---

## Próximos Passos de Implementação (Roadmap)

1. **Passo 1: Modelagem Relacional (PostgreSQL / Supabase):**
   - Criação do script DDL com integridade referencial, foreign keys e timestamps para as entidades: `tutores`, `pets`, `colaboradores`, `produtos`, `servicos`, `compras`, `itens_compra`, `atendimentos`, `insumos_atendimento`, `vendas`, `itens_venda`, `movimentacoes_estoque`, `financeiro_lancamentos`.
2. **Passo 2: Arquitetura do Repositório Python:**
   - Estruturação em camadas (`src/config/`, `src/database/`, `src/services/`, `src/views/` ou `pages/`).
3. **Passo 3: Módulos Operacionais e Autenticação Google:**
   - Configuração do Google Auth com Streamlit Secrets.
   - Interface com fluxo de caixa rápido (PDV), esteira de banho e tosa, compras e estoque.
4. **Passo 4: Seed de Dados:**
   - Script para popular o banco no Supabase com massa de dados realista para testes e validação da 1ª e 2ª VA.
