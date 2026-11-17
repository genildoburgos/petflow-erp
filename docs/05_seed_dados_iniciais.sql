-- ==============================================================================
-- CARGA INICIAL DE DADOS (SEED DATA): PetFlow ERP
-- Compatível com o Modelo Integrado (HVU / UFAPE + ERP Completo)
-- ==============================================================================

-- 1. Endereços
INSERT INTO enderecos (cep, rua, numero, bairro, cidade, uf) VALUES
('55290-000', 'Av. Rui Barbosa', '450', 'Heliópolis', 'Garanhuns', 'PE'),
('55295-100', 'Rua São Pedro', '88', 'Boa Vista', 'Garanhuns', 'PE'),
('55292-200', 'Rua Doutor José Mariano', '120', 'Centro', 'Garanhuns', 'PE'),
('55000-000', 'Rodovia BR-423', 'Km 92', 'Distrito Industrial', 'Garanhuns', 'PE')
ON CONFLICT DO NOTHING;

-- 2. Espécies (Padrão HVU)
INSERT INTO especies (nome, descricao) VALUES
('Canina', 'Cães domésticos de todos os portes e raças'),
('Felina', 'Gatos domésticos'),
('Silvestre / Exóticos', 'Aves, roedores e pequenos animais não convencionais')
ON CONFLICT (nome) DO NOTHING;

-- 3. Raças (Padrão HVU com Porte)
INSERT INTO racas (especie_id, nome, porte, descricao) VALUES
(1, 'SRD - Sem Raça Definida', 'Médio', 'Cão vira-lata de porte médio'),
(1, 'Golden Retriever', 'Grande', 'Pelagem longa e densa, dócil'),
(1, 'Shih Tzu', 'Pequeno', 'Pelagem longa, necessita tosa frequente'),
(1, 'Spitz Alemão (Lulu da Pomerânia)', 'Pequeno', 'Pelagem dupla, sensível a tosa na máquina'),
(1, 'Pastor Alemão', 'Grande', 'Porte atlético e pelagem densa'),
(1, 'Pinscher Miniatura', 'Mini', 'Pequeno porte, pelo curto'),
(2, 'SRD Felino', 'Pequeno', 'Gato comum europeu/brasileiro'),
(2, 'Siamês', 'Pequeno', 'Pelo curto com extremidades escuras'),
(2, 'Persa', 'Médio', 'Pelo longo que requer escovação diária')
ON CONFLICT (especie_id, nome) DO NOTHING;

-- 4. Tutores (Padrão HVU)
INSERT INTO tutores (endereco_id, nome, cpf, rg, telefone, email, observacoes) VALUES
(1, 'Ana Clara Mendonça', '111.222.333-44', '8.999.111 SDS/PE', '(87) 98888-1122', 'ana.clara@email.com', 'Tutor exigente com horário de banho'),
(2, 'Bruno Silveira', '222.333.444-55', '7.888.222 SSP/PE', '(87) 98888-2233', 'bruno.silva@email.com', 'Cliente de vacinas periódicas'),
(3, 'Camila Rodrigues', '333.444.555-66', '6.777.333 SDS/PE', '(87) 98888-3344', 'camila.vet@email.com', 'Tutora de gato com alergia alimentar')
ON CONFLICT DO NOTHING;

-- 5. Animais / Pacientes (Padrão HVU com Prontuário, Castrado, Peso)
INSERT INTO animais (tutor_id, raca_id, codigo_prontuario, nome, sexo, castrado, peso, data_nascimento, alergias) VALUES
(1, 2, 'PRONT-2026-0001', 'Thor', 'M', TRUE, 32.50, '2023-04-10', 'Sensibilidade cutânea a fragrâncias cítricas'),
(1, 3, 'PRONT-2026-0002', 'Luna', 'F', TRUE, 5.80, '2024-01-15', 'Nenhuma alergia conhecida'),
(2, 1, 'PRONT-2026-0003', 'Bob', 'M', FALSE, 14.20, '2022-08-20', 'Medo intenso de secador no rosto e focinheira'),
(3, 8, 'PRONT-2026-0004', 'Mimi', 'F', TRUE, 3.80, '2023-11-05', 'Intolerância a rações com corante')
ON CONFLICT (codigo_prontuario) DO NOTHING;

-- 6. Colaboradores (Com CRMV para Vets, Comissão e Vínculo com Google Auth)
INSERT INTO colaboradores (nome, cpf, telefone, email, auth_email, cargo, crmv, percentual_comissao) VALUES
('Dra. Juliana Aguiar', '011.222.333-99', '(87) 99333-4455', 'juliana.vet@petflow.com', 'juliana.vet@gmail.com', 'VETERINARIO', 'CRMV-PE 12345', 40.00),
('Carla Tosadora', '022.333.444-88', '(87) 99111-2233', 'carla.tosa@petflow.com', 'carla.tosa@gmail.com', 'TOSADOR', NULL, 30.00),
('Marcos Banhista', '033.444.555-77', '(87) 99222-3344', 'marcos.banho@petflow.com', 'marcos.banho@gmail.com', 'BANHISTA', NULL, 20.00),
('Fernanda Recepção', '044.555.666-66', '(87) 99444-5566', 'fernanda.caixa@petflow.com', 'fernanda.caixa@gmail.com', 'RECEPCIONISTA', NULL, 0.00),
('Administrador Geral', '000.111.222-33', '(87) 99999-0000', 'admin@petflow.com', 'admin@petflow.com', 'GERENTE', NULL, 0.00)
ON CONFLICT (cpf) DO NOTHING;

-- 7. Fornecedores
INSERT INTO fornecedores (endereco_id, razao_social, nome_fantasia, cnpj, telefone, email, contato_nome) VALUES
(4, 'Distribuidora Pet Agreste LTDA', 'Pet Agreste Distribuição', '12.345.678/0001-90', '(87) 3761-9900', 'pedidos@petagreste.com.br', 'Roberto Vendas'),
(4, 'Zoovet Farmacêutica Animal SA', 'Zoovet Saúde Animal', '98.765.432/0001-10', '(81) 3456-7890', 'comercial@zoovet.com.br', 'Mariana Lab')
ON CONFLICT (cnpj) DO NOTHING;

-- 8. Categorias
INSERT INTO categorias (nome, tipo) VALUES
('Estética Animal', 'SERVICO'),
('Clínica & Veterinária', 'SERVICO'),
('Rações & Nutrição', 'PRODUTO'),
('Cosméticos & Higiene', 'PRODUTO'),
('Medicamentos & Vacinas', 'PRODUTO'),
('Acessórios & Petiscos', 'PRODUTO')
ON CONFLICT (nome) DO NOTHING;

-- 9. Serviços (Estética e Clínica)
INSERT INTO servicos (categoria_id, nome, tipo_servico, preco_base, duracao_minutos) VALUES
(1, 'Banho Completo (Porte Pequeno)', 'ESTETICA', 65.00, 45),
(1, 'Banho Completo (Porte Médio)', 'ESTETICA', 80.00, 60),
(1, 'Banho Completo (Porte Grande)', 'ESTETICA', 110.00, 80),
(1, 'Tosa Higiênica Adicional', 'ESTETICA', 30.00, 20),
(1, 'Tosa Geral na Máquina', 'ESTETICA', 90.00, 60),
(1, 'Tosa na Tesoura Especializada', 'ESTETICA', 140.00, 90),
(2, 'Consulta Veterinária Geral', 'CLINICO', 150.00, 45),
(2, 'Consulta Veterinária de Retorno', 'CLINICO', 80.00, 30),
(2, 'Aplicação de Vacina V10 Importada', 'CLINICO', 110.00, 20),
(2, 'Aplicação de Vacina Antirrábica', 'CLINICO', 75.00, 15)
ON CONFLICT DO NOTHING;

-- 10. Produtos (Insumos de Consumo e Itens de Revenda)
INSERT INTO produtos (categoria_id, codigo_barras, nome, tipo_produto, unidade_medida, preco_custo, preco_venda, estoque_minimo, estoque_atual) VALUES
(4, '78910001', 'Shampoo Neutro Hipoalergênico 5L', 'INSUMO_OPERACIONAL', 'L', 85.00, 0.00, 2.00, 5.00),
(4, '78910002', 'Condicionador Pelos Macios 5L', 'INSUMO_OPERACIONAL', 'L', 95.00, 0.00, 2.00, 3.00),
(5, '78910003', 'Vacina V10 Canina Vanguard Plus (Dose)', 'INSUMO_OPERACIONAL', 'DOSE', 42.00, 0.00, 10.00, 20.00),
(3, '78910004', 'Ração Golden Special Frango & Carne 15kg', 'REVENDA', 'PCT', 142.00, 189.90, 5.00, 14.00),
(3, '78910005', 'Ração Premier Formula Cães Pequenos 2.5kg', 'REVENDA', 'PCT', 68.00, 94.90, 4.00, 9.00),
(3, '78910006', 'Sachê Whiskas Carne para Gatos 85g', 'REVENDA', 'UN', 2.40, 4.50, 20.00, 50.00),
(5, '78910007', 'Simparic 20mg Cães 5 a 10kg (1 comp)', 'AMBOS', 'UN', 72.00, 108.00, 5.00, 10.00),
(6, '78910008', 'Petisco Bifinho Keldog Carne 500g', 'REVENDA', 'PCT', 12.50, 21.90, 8.00, 18.00)
ON CONFLICT (codigo_barras) DO NOTHING;

-- 11. Medicamentos (Catálogo para Prescrição - Base HVU)
INSERT INTO medicamentos (nome, principio_ativo, concentracao, via_administracao, detalhes) VALUES
('Gaviz V', 'Omeprazol', '10mg', 'Oral', 'Protetor gástrico para cães e gatos'),
('Prediderm', 'Prednisolona', '5mg', 'Oral', 'Anti-inflamatório esteroide'),
('Synulox', 'Amoxicilina + Clavulanato', '50mg', 'Oral', 'Antibiótico de amplo espectro'),
('Otodem Plus', 'Cetoconazol + Gentamicina', 'Frasco 20ml', 'Otológica', 'Solução para otites bacterianas e fúngicas'),
('Apoquel', 'Maleato de Oclacitinib', '5.4mg', 'Oral', 'Antipruriginoso para dermatites alérgicas')
ON CONFLICT DO NOTHING;

-- 12. Atendimento Estético Exemplo (Com Check-in de Segurança)
INSERT INTO atendimentos_estetica (
    numero_os, animal_id, servico_id, colaborador_id, status, 
    valor_servico, percentual_comissao, tem_pulgas, tem_nos_pelagem, tem_ferimento_previo, observacoes_manejo
) VALUES (
    'OS-202611-0001', 1, 3, 2, 'FINALIZADO_ENTREGUE', 
    110.00, 30.00, FALSE, TRUE, FALSE, 'Thor estava com nós nas patas traseiras; tosa cuidadosa realizada.'
) ON CONFLICT (numero_os) DO NOTHING;

-- 13. Consulta Veterinária Exemplo (Prontuário HVU + Prescrição)
INSERT INTO consultas_veterinarias (
    numero_consulta, animal_id, veterinario_id, peso_atual, idade_atual_meses,
    queixa_principal, tipo_consulta, alteracoes_clinicas_diversas, suspeitas_clinicas, alimentacao,
    temperatura_celsius, frequencia_cardiaca_bpm, frequencia_respiratoria_mpm, tpc_segundos,
    parecer_diagnostico, valor_consulta, percentual_comissao, status
) VALUES (
    'CONS-202611-0001', 3, 1, 14.20, 26,
    'Animal coçando muito a orelha direita e sacudindo a cabeça há 3 dias.', 'PRIMEIRA_VEZ',
    'Presença de secreção ceruminosa escura e odor fétido no conduto auditivo direito.',
    'Otite externa fúngica/bacteriana.', 'Ração Golden cães adultos',
    38.6, 115, 26, 2,
    'Otite externa unilateral; indicado limpeza e Otodem Plus 2x/dia por 10 dias.', 150.00, 40.00, 'FINALIZADA'
) ON CONFLICT (numero_consulta) DO NOTHING;

-- Prescrição vinculada à consulta acima
INSERT INTO prescricoes (consulta_id, medicamento_id, dose, frequencia, periodo_dias, observacoes_administracao) VALUES
(1, 4, '4 gotas em cada conduto', 'A cada 12 horas', 10, 'Limpar o ouvido com algodão seco antes de pingar as gotas.')
ON CONFLICT DO NOTHING;

-- 14. Vendas Exemplo (PDV Balcão - Integração com Atendimento)
INSERT INTO vendas (
    numero_venda, tutor_id, atendimento_estetica_id, colaborador_caixa_id,
    subtotal, desconto, valor_total, forma_pagamento, status
) VALUES (
    'VENDA-202611-0001', 1, 1, 4,
    110.00, 0.00, 110.00, 'PIX', 'FINALIZADA'
) ON CONFLICT (numero_venda) DO NOTHING;

-- 15. Lançamentos Financeiros (Fluxo de Caixa Alimentado)
INSERT INTO financeiro_lancamentos (
    tipo, categoria_financeira, descricao, valor, status, forma_pagamento, origem_modulo, origem_id
) VALUES 
('RECEITA', 'SERVICO_ESTETICA', 'Recebimento Banho Thor - OS-202611-0001', 110.00, 'PAGO', 'PIX', 'VENDAS', 1),
('RECEITA', 'CONSULTA_CLINICA', 'Recebimento Consulta Bob - CONS-202611-0001', 150.00, 'PAGO', 'CARTAO_DEBITO', 'CLINICA', 1),
('DESPESA', 'COMISSAO_COLABORADOR', 'Comissão Carla Tosadora - OS-202611-0001', 33.00, 'PENDENTE', 'PIX', 'ESTETICA', 1),
('DESPESA', 'COMISSAO_COLABORADOR', 'Comissão Dra. Juliana Vet - CONS-202611-0001', 60.00, 'PENDENTE', 'PIX', 'CLINICA', 1)
ON CONFLICT DO NOTHING;
