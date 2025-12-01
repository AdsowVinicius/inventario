-- ====================================
-- Dados de Exemplo para Sistema de Inventário
-- Execute APÓS criar as tabelas
-- ====================================

USE inventario;

-- ====================================
-- Inserir Itens de Inventário
-- ====================================

INSERT INTO itens_inventario (num_material, txt_descrica_material, planta, deposito, tipo_material, und_medida)
VALUES 
    -- Planta PS01
    ('PN-001', 'Parafuso M8x20', 'PS01', 'DEP-01', 'FIXACAO', 'UN'),
    ('PN-002', 'Porca M8', 'PS01', 'DEP-01', 'FIXACAO', 'UN'),
    ('PN-003', 'Arruela Lisa M8', 'PS01', 'DEP-01', 'FIXACAO', 'UN'),
    ('PN-004', 'Cabo Elétrico 2,5mm', 'PS01', 'DEP-02', 'ELETRICO', 'M'),
    ('PN-005', 'Disjuntor 20A', 'PS01', 'DEP-02', 'ELETRICO', 'UN'),
    
    -- Planta PS02
    ('PN-006', 'Válvula Esfera 1/2"', 'PS02', 'DEP-03', 'HIDRAULICO', 'UN'),
    ('PN-007', 'Tubo PVC 25mm', 'PS02', 'DEP-03', 'HIDRAULICO', 'M'),
    ('PN-008', 'Cotovelo PVC 90º 25mm', 'PS02', 'DEP-03', 'HIDRAULICO', 'UN'),
    ('PN-009', 'Filtro de Água', 'PS02', 'DEP-04', 'FILTRAGEM', 'UN'),
    
    -- Planta PS03
    ('PN-010', 'Rolamento 6205', 'PS03', 'DEP-05', 'MECANICO', 'UN'),
    ('PN-011', 'Correia Tipo A', 'PS03', 'DEP-05', 'MECANICO', 'UN'),
    ('PN-012', 'Lubrificante SAE 30', 'PS03', 'DEP-06', 'LUBRIFICANTE', 'L'),
    ('PN-013', 'Graxa Litio', 'PS03', 'DEP-06', 'LUBRIFICANTE', 'KG'),
    
    -- Planta PS05
    ('PN-014', 'Sensor Temperatura', 'PS05', 'DEP-07', 'ELETRONICO', 'UN'),
    ('PN-015', 'Relé 12V', 'PS05', 'DEP-07', 'ELETRONICO', 'UN'),
    ('PN-016', 'LED Verde 5mm', 'PS05', 'DEP-08', 'ELETRONICO', 'UN'),
    ('PN-017', 'Resistor 1K Ohm', 'PS05', 'DEP-08', 'ELETRONICO', 'UN'),
    
    -- Planta PS09
    ('PN-018', 'Chapa Aço 1mm', 'PS09', 'DEP-09', 'MATERIA-PRIMA', 'M2'),
    ('PN-019', 'Perfil U 50mm', 'PS09', 'DEP-09', 'MATERIA-PRIMA', 'M'),
    ('PN-020', 'Solda MIG', 'PS09', 'DEP-10', 'CONSUMIVEL', 'KG'),
    
    -- Planta PB82
    ('PN-021', 'Tinta Branca 18L', 'PB82', 'DEP-11', 'ACABAMENTO', 'UN'),
    ('PN-022', 'Lixa Grão 80', 'PB82', 'DEP-11', 'ACABAMENTO', 'UN'),
    ('PN-023', 'Pincel 2"', 'PB82', 'DEP-12', 'FERRAMENTA', 'UN'),
    ('PN-024', 'Rolo Espuma', 'PB82', 'DEP-12', 'FERRAMENTA', 'UN'),
    ('PN-025', 'Massa Corrida 5KG', 'PB82', 'DEP-11', 'ACABAMENTO', 'UN');

-- ====================================
-- Verificar inserção
-- ====================================

SELECT COUNT(*) AS 'Total de Itens Inseridos' FROM itens_inventario;

SELECT planta, COUNT(*) AS 'Quantidade'
FROM itens_inventario
GROUP BY planta
ORDER BY planta;

-- ====================================
-- Exemplos de Consultas Úteis
-- ====================================

-- Listar todos os part numbers de uma planta
-- SELECT num_material, txt_descrica_material 
-- FROM itens_inventario 
-- WHERE planta = 'PS01';

-- Contar itens por tipo
-- SELECT tipo_material, COUNT(*) AS quantidade
-- FROM itens_inventario
-- GROUP BY tipo_material
-- ORDER BY quantidade DESC;

SELECT 'Dados de exemplo inseridos com sucesso!' AS status;
