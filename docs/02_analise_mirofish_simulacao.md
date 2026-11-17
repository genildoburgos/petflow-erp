# Análise da Simulação MiroFish: Dinâmica Social & Dores Crônicas do Setor Pet

> **Referência da Simulação:** `sim_78ccf9a47b13` / Projeto `proj_4f4175b49755`  
> **Arquivo Seed Original:** `seed_pesquisa_04_erp_pet_veterinaria.txt`  
> **Motor de Simulação:** MiroFish / OASIS Multi-Agent Social Simulation  
> **Escopo Temporal:** 72 horas simuladas (3 dias com foco em rotina de abertura, dias úteis e pico de sábado pela manhã no fuso horário UTC-3).

---

## 1. Composição do Ecossistema de Personas (25 Agentes)

A simulação mapeou 6 grupos de interesse interdependentes:
1. **Dono de Pet Shop / Empreendedor:** O gestor central que apaga incêndios, sofre com reajustes de software e perde finais de semana conferindo comissões.
2. **Recepcionista / Operadora de Caixa:** Sofre a pressão direta da fila de atendimento no sábado de manhã, lentidão do sistema e cadastro burocrático.
3. **Tosador / Banhista (Groomer):** Remunerado por produção (comissão), desconfia dos relatórios fechados pelo patrão em pacotes promocionais.
4. **Médica Veterinária Autônoma / Pequena Clínica:** Precisa prescrever rápido, registrar vacinas e odeia ter que preencher 50 campos de anamnese.
5. **Tutor de Pet (Cliente Final):** Exige saber o status do animal em tempo real, quer lembretes de vacina por WhatsApp e transparência no valor pago.
6. **Vendedores / Fornecedores de Software (Incumbentes):** Representando as defesas tradicionais de mercado ("nosso sistema é completo", "basta fazer o treinamento").

---

## 2. Padrões de Comportamento e Citações Reais Extraídas da Simulação

A simulação gerou dezenas de debates ricos no Reddit e Twitter simulados. A seguir, os principais padrões identificados:

### A. O Colapso do Sábado de Manhã (Recepcionistas & Donos)
> *"Sábado de manhã, fila no balcão, e o SimplesVet travando para abrir a agenda de banho. Cada clique demora uma eternidade. Enquanto isso, o cliente espera e o telefone não para. Alguém mais passa por isso?"*  
> **Reação da Comunidade:** Consenso de que nos sábados, mais de 60% da receita de estética é gerada e os sistemas em nuvem apresentam latência elevada, obrigando a recepcionista a anotar em papel de rascunho para lançar horas depois.

### B. O "Buraco Negro" dos Pacotes Promocionais e Comissões (Tosadores & Donos)
> *"Passo a madrugada conferindo planilha de comissão porque o sistema não calcula direito o pacote 'compre 4 banhos, ganhe 1 hidratação'. O tosador recebe errado, eu pago errado e ninguém confia no número. SimplesVet e Vetus falham nisso."*  
> **Reação dos Tosadores:**  
> *"Aqui no banho e tosa é exatamente isso. O pacote 'compre 4, ganhe 1' vira dor de cabeça na hora de fechar a comissão. Na cabeça do patrão a gente tem que receber menos porque deu desconto pro cliente, mas o meu trabalho no pelo do cachorro foi o mesmo!"*  
> **Insight Chave de Produto:** O sistema precisa separar explicitamente o **Desconto Comercial concedido ao cliente** da **Base de Cálculo da Mão de Obra do profissional**.

### C. A Veterinária Pequena vs. O Software Hospitalar
> *"Trabalho em uma clínica pequena, dois plantões por semana. O Vetus é pesado, desktop, cheio de parametrização. Para emitir uma receita simples e marcar a vacina, perco 10 minutos preenchendo campos que nunca vou usar."*  
> **Insight Chave de Produto:** Clínicas de 1 a 2 salas precisam de um prontuário ágil em formato SOAP (Subjetivo, Objetivo, Avaliação, Plano) focado em histórico vacinal, receituário limpo e lembrete automático de retorno.

### D. As Gambiarras Atuais (Como o setor sobrevive hoje)
A simulação revelou as 4 maiores "gambiarras" utilizadas pelos pequenos estabelecimentos para contornar os sistemas legados:
1. **WhatsApp Web aberto em 3 abas** com atendentes digitando mensagens manuais para avisar que o cachorro está pronto.
2. **Caderninho físico de fiado / comanda de balcão** para não travar a fila do sábado.
3. **Planilha paralela em Excel/Google Sheets** rodando exclusivamente para cálculo de comissões semanais dos tosadores.
4. **Fita crepe na gaiola do pet** com anotações à caneta (*"alérgico a perfume"*, *"tosar baixo"*), pois o tosador não tem acesso ou tempo de abrir o cadastro do animal no computador.

---

## 3. Matriz "Kill vs. Keep": O que Cortar e o que Lapidar no MVP

Com base na síntese dos dados do MiroFish e da pesquisa de concorrentes:

```mermaid
quadrantChart
    title Priorização do MVP (MiroFish Insights)
    x-axis Baixa Urgência --> Alta Urgência
    y-axis Complexidade Alta --> Complexidade Baixa
    quadrant-1 Ouro do MVP (Fazer Imediatamente)
    quadrant-2 Planejar com Cuidado (Valor Alto, Complexo)
    quadrant-3 Eliminar / Matar (Desnecessário no MVP)
    quadrant-4 Recursos Básicos (Fazer Rápido)
    "PDV Balcão Rápido": [0.92, 0.85]
    "Agenda Banho/Tosa Visual": [0.88, 0.80]
    "Comissões Automáticas de Tosador": [0.85, 0.70]
    "Check-in Visual com Fotos": [0.78, 0.65]
    "Status de WhatsApp (1 clique)": [0.75, 0.60]
    "Prontuário Clínico SOAP Básico": [0.70, 0.75]
    "Controle de Insumos (Shampoo/Vacina)": [0.65, 0.55]
    "Módulo de Internação UTI Hospitalar": [0.15, 0.15]
    "Emissão de NFSe com 30 tributações": [0.40, 0.20]
    "Controle de Hotel/Creche complexo": [0.35, 0.30]
    "Cobrança por usuário": [0.05, 0.90]
```

### O que ELIMINAR impiedosamente (O que os outros fazem errado):
- ❌ **Módulos hospitalares densos:** Fichas de anestesia complexa, internação UTI e rateio de centro de custo avançado.
- ❌ **Bloqueio de cadastro:** Obrigatoriedade de preencher CPF, RG, endereço e microchip para conseguir vender um pacote de ração no balcão.
- ❌ **Cobrança de licença por assento:** Usuários ilimitados para encorajar cada membro da equipe a ter seu próprio login (aumentando a rastreabilidade das operações).

### O que MANTER e lapidar como diferencial:
-  **Agenda Visual Rápida:** Status claros (*Chegou, Em Banho, Pronto, Entregue*).
-  **Checkout em 1 Tela:** Lança o serviço do pet + produtos de balcão e liquida no caixa em segundos.
-  **Cálculo Automático de Comissões:** Transparência total para tosador e dono.
-  **Baixa Automática de Insumos:** Banho consome shampoo; vacina aplicada consome o lote da geladeira.
