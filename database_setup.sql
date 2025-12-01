-- ====================================
-- Script SQL para Sistema de Inventário
-- MariaDB / MySQL
-- ====================================

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS inventario 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE inventario;

-- ====================================
-- Tabela: user_table
-- ====================================
CREATE TABLE IF NOT EXISTS user_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    planta ENUM('PS01', 'PS02', 'PS03', 'PS05', 'PS09', 'PB82') NOT NULL,
    role ENUM('ADMIN', 'ENCARREGADO', 'CONTADOR') NOT NULL DEFAULT 'CONTADOR',
    INDEX idx_user_name (user_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================
-- Tabela: itens_inventario
-- ====================================
CREATE TABLE IF NOT EXISTS itens_inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    num_material VARCHAR(50) NOT NULL,
    txt_descrica_material VARCHAR(255),
    planta VARCHAR(10) NOT NULL,
    deposito VARCHAR(50),
    tipo_material VARCHAR(50),
    und_medida VARCHAR(10),
    INDEX idx_num_material (num_material),
    INDEX idx_planta (planta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================
-- Tabela: forms_contagem
-- ====================================
CREATE TABLE IF NOT EXISTS forms_contagem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    planta VARCHAR(10) NOT NULL,
    num_contagem INT NOT NULL,
    zona_inventario VARCHAR(50) NOT NULL,
    etiqueta_inventario VARCHAR(50) NOT NULL,
    part_number VARCHAR(50) NOT NULL,
    campo VARCHAR(100),
    qtd FLOAT NOT NULL DEFAULT 0.0,
    usuario_id INT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_planta (planta),
    INDEX idx_num_contagem (num_contagem),
    INDEX idx_zona (zona_inventario),
    INDEX idx_etiqueta (etiqueta_inventario),
    INDEX idx_part_number (part_number),
    FOREIGN KEY (usuario_id) REFERENCES user_table(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====================================
-- Dados de exemplo (opcional)
-- ====================================

-- Inserir alguns itens de exemplo
INSERT INTO itens_inventario (num_material, txt_descrica_material, planta, deposito, tipo_material, und_medida)
VALUES 
    ('MAT-001', 'Material Teste 1', 'PS01', 'DEP01', 'TIPO-A', 'UN'),
    ('MAT-002', 'Material Teste 2', 'PS01', 'DEP01', 'TIPO-B', 'KG'),
    ('MAT-003', 'Material Teste 3', 'PS02', 'DEP02', 'TIPO-A', 'M'),
    ('MAT-004', 'Material Teste 4', 'PS03', 'DEP03', 'TIPO-C', 'UN');

-- ====================================
-- Verificar criação das tabelas
-- ====================================
SHOW TABLES;

-- Ver estrutura das tabelas
DESCRIBE user_table;
DESCRIBE itens_inventario;
DESCRIBE forms_contagem;

SELECT 'Database setup completed successfully!' AS status;
