# Comparativo Arquitetural: Sistema HVU (UFAPE/LMTS) vs. PetFlow ERP

> **Documento de Decisões de Arquitetura de Dados (ADR)**  
> **Referência Real:** Projeto HVU (`https://github.com/genildoburgos/hvu.git`), migrações Flyway V1 a V31 e Diagrama de Classes.

---

## 1. Contexto e Motivação

O **HVU (Hospital Veterinário Universitário)** é um sistema em produção desenvolvido no Laboratório Multidisciplinar de Tecnologias Sociais (LMTS) da UFAPE para apoiar o atendimento hospitalar e o ensino prático do curso de Medicina Veterinária.

Ao projetar o **PetFlow ERP** para a disciplina de Sistemas de Informação e Tecnologias (Prof. Dr. Assuero Ximenes), foi realizado um alinhamento direto com o modelo do HVU para:
1. **Adotar boas práticas reais de modelagem do domínio veterinário** (eliminando amadorismo ou simplificações artificiais).
2. **Harmonizar a gestão clínica com a gestão comercial/financeira** exigida pelo edital do ERP (compras, estoque, vendas e fluxo de caixa).

---

## 2. Decisões de Modelagem Incorporadas do HVU

### 2.1 Normalização de Espécies e Raças
* **Como era na v1 preliminar:** Strings livres no cadastro do pet (`especie VARCHAR`, `raca VARCHAR`).
* **Como é no HVU:** Entidades `especie` e `raca` separadas, com chave estrangeira e vínculo de porte na raça.
* **Decisão Adotada no PetFlow:** Tabelas `especies` e `racas` normalizadas, garantindo integridade referencial e prevenindo inconsistências textuais no banco.

### 2.2 Entidade Endereço Normalizada
* **Como é no HVU:** Entidade `endereco` com CEP, logradouro, número, bairro e cidade associada ao usuário.
* **Decisão Adotada no PetFlow:** Tabela `enderecos` que atende tanto a Tutores quanto a Fornecedores.

### 2.3 Atributos Clínicos Reais do Animal
* **Incorporado do HVU:**
  * `codigo_prontuario` único gerado sequencialmente.
  * `castrado` (BOOLEAN): essencial para dosagem de medicamentos e manejo comportamental.
  * `peso` (NUMERIC): base para cálculo de dosagens e definição de preço de banho.
  * `obito` (BOOLEAN): controle histórico para desativação de lembretes e agendamentos.

### 2.4 Ficha Clínica Completa & Receituário (Prescrição)
* **Incorporado do HVU:**
  * Divisão da anamnese em `queixa_principal`, `alteracoes_clinicas_diversas`, `suspeitas_clinicas` e `alimentacao`.
  * Registro de sinais vitais na consulta (`temperatura_celsius`, `frequencia_cardiaca_bpm`, `frequencia_respiratoria_mpm`, `tpc_segundos`, `nivel_consciencia`, `nivel_hidratacao`, `tipo_mucosa`).
  * Tabela de `medicamentos` e `prescricoes` associadas à consulta (dose, frequência e período em dias).

---

## 3. As Extensões de ERP (O que o HVU não possui e nosso ERP implementa)

O HVU é um sistema estritamente clínico-hospitalar público. Para atender ao edital da 1ª VA da UFAPE, o PetFlow ERP complementa o modelo com:
1. **Módulo de Compras:** Entrada de notas de fornecedores alimentando estoque e contas a pagar.
2. **Módulo de Estética Animal:** Esteira ágil de Banho & Tosa com check-in de segurança visual e comissões automáticas.
3. **Módulo de Vendas (PDV Balcão):** Caixa rápido em 1 tela que fatura atendimentos e itens de revenda.
4. **Módulo de Estoque Transacional:** Movimentações com `estoque_anterior`, `estoque_posterior` e rastreabilidade de origem.
5. **Módulo Financeiro:** DRE simplificado, fluxo de caixa diário e extrato de comissões.
6. **5 Views Analíticas:** Base preparada para o Dashboard de BI da 2ª VA.
