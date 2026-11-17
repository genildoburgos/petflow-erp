# 🛡️ Revisão de Qualidade, Hardening & Auditoria Arquitetural (Quality Gate)

> **Documento:** 06_revisao_qualidade_e_hardening.md  
> **Projeto:** PetFlow ERP (Sistemas de Informação 2026.2 - UFAPE)  
> **Referência Externa:** Auditoria cruzada via Modo IA (Quality Gate Pré-Entrega)  
> **Data:** Novembro de 2026  

---

## 1. Contexto e Motivação

Antes de submeter o sistema para a avaliação da 1ª VA, o código e a arquitetura foram submetidos a um agente externo de inteligência artificial especializado em engenharia de software para atuar como **Quality Gate**. 

O objetivo foi identificar precocemente potenciais armadilhas de concorrência, esgotamento de conexões, vazamento de privilégios ou perda de precisão monetária ao combinar a stack: **Python + Streamlit + PostgreSQL (Supabase)**.

O auditor externo validou a arquitetura como **"excelente"**, destacando a separação estrita de camadas (`services/` vs `views/`), a integridade com travas em nível de linha (`SELECT FOR UPDATE`) e a navegação nativa via `st.navigation`. Simultaneamente, levantou 4 pontos de atenção cruciais que foram imediatamente endereçados através de ações de *hardening*.

---

## 2. Matriz de Análise & Ações de Hardening

| # | Ponto Crítico Levantado pelo Quality Gate | Risco Identificado | Ação de Hardening Aplicada no PetFlow |
| :--- | :--- | :--- | :--- |
| **1** | **Precisão Monetária (`Decimal` vs `float`)** | Números em ponto flutuante (`float`) no Python acumulam dízimas binárias (`0.1 + 0.2 = 0.30000000000000004`), causando divergência de centavos em totais, descontos e comissões. | Criação do módulo `src/utils/money.py` implementando `Decimal` e arredondamento comercial `ROUND_HALF_UP`. Refatoração de `venda_service.py`, `compra_service.py` e `atendimento_service.py`. |
| **2** | **Connection Pooling no Supabase (Porta 6543 vs 5432)** | O Streamlit reexecuta o script a cada interação. Conexões diretas (porta 5432) podem esgotar rapidamente as ~60 conexões do plano gratuito do Supabase. | Configuração do `connection.py` com desativação de *prepared statements* (`prepare_threshold: None` no psycopg v3) para operar de forma transparente com o Transaction Pooler (porta 6543 / Supavisor / PgBouncer). |
| **3** | **Risco no Fallback de Autenticação (`auth_manager.py`)** | Um fallback automático irrestrito para administrador em produção concederia acesso total a qualquer visitante. | O fallback foi formalizado como **Modo de Avaliação Acadêmica (1ª VA)**, ativado por flag de configuração (`allow_evaluator_fallback`), identificado por badge visual claro e acompanhado por um **Simulador de Personas** na barra lateral. |
| **4** | **Invalidação de Cache e Re-execução no Streamlit** | Se consultas de estoque ou caixa fossem cacheadas com `@st.cache_data` sem expiração ou limpeza, o operador veria saldo desatualizado após uma venda. | O PetFlow ERP mantém consultas de leitura transacional diretas com limites (`LIMIT`), acionando `st.rerun()` cirurgicamente após mutações, garantindo que o saldo seja recalculado em tempo real sem dados defasados. |
| **5** | **Auditoria Imutável e Rastreabilidade** | Falta de visibilidade de quem alterou o estoque ou lançou movimentações financeiras. | Manutenção do padrão append-only na tabela `movimentacoes_estoque`, registrando saldo anterior, novo saldo, módulo de origem e justificativa de cada operação. |

---

## 3. Otimizações de Engenharia Implementadas

### 3.1. Precisão Numérica com `src/utils/money.py`
```python
from decimal import Decimal, ROUND_HALF_UP

def to_decimal(val) -> Decimal:
    if val is None:
        return Decimal("0.00")
    if isinstance(val, (int, str)):
        return Decimal(str(val))
    if isinstance(val, float):
        return Decimal(f"{val:.4f}")
    return Decimal(str(val))

def round_money(val) -> Decimal:
    return to_decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

### 3.2. Conexão Resiliente com PgBouncer (`src/database/connection.py`)
```python
connect_args = {}
if "psycopg" in db_url and "psycopg2" not in db_url:
    # Desativa prepared statements em transaction mode pooler
    connect_args["prepare_threshold"] = None

engine = create_engine(
    db_url,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args=connect_args
)
```

### 3.3. Simulador de Personas para a Apresentação Acadêmica
Para demonstrar ao Prof. Dr. Assuero o controle de acesso e cálculo diferencial de comissões, a barra lateral permite alternar entre:
- **Dra. Camila:** Médica Veterinária (CRMV-PE 4821, 30% comissão).
- **Lucas Ramos:** Tosador e Esteticista Pet (20% comissão).
- **Mariana Duarte:** Operadora de Caixa / Frente de Vendas.
- **Roberto Santos:** Gerente Geral e Administrador do Sistema.

---

## 4. Conclusão

Com a incorporação dessas diretrizes do Quality Gate, o PetFlow ERP atinge maturidade técnica alinhada aos padrões de sistemas de informação corporativos, protegendo a integridade do banco de dados, garantindo precisão contábil e proporcionando uma experiência de avaliação interativa para a banca da UFAPE.
