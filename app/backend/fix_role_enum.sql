-- Script para corrigir o enum de roles na tabela user_table
USE inventario;

-- Alterar a coluna role para usar valores maiúsculos
ALTER TABLE user_table 
MODIFY COLUMN role ENUM('ADMIN', 'ENCARREGADO', 'CONTADOR') NOT NULL DEFAULT 'CONTADOR';

-- Atualizar valores existentes para maiúsculo
UPDATE user_table SET role = 'ADMIN' WHERE role = 'admin';
UPDATE user_table SET role = 'ENCARREGADO' WHERE role = 'encarregado';
UPDATE user_table SET role = 'CONTADOR' WHERE role = 'contador';

SELECT 'Role enum atualizado com sucesso!' AS status;
SELECT * FROM user_table;
