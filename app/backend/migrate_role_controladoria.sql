-- Script para alterar ENCARREGADO para CONTROLADORIA
-- Execute este script no MySQL para atualizar a tabela de usuários

-- 1. Primeiro, adicionar CONTROLADORIA ao ENUM (temporariamente ter ambos)
ALTER TABLE user_table 
MODIFY COLUMN role ENUM('ADMIN', 'ENCARREGADO', 'CONTROLADORIA', 'CONTADOR') 
NOT NULL DEFAULT 'CONTADOR';

-- 2. Atualizar todos os usuários ENCARREGADO para CONTROLADORIA
UPDATE user_table 
SET role = 'CONTROLADORIA' 
WHERE role = 'ENCARREGADO';

-- 3. Remover ENCARREGADO do ENUM (deixar apenas os válidos)
ALTER TABLE user_table 
MODIFY COLUMN role ENUM('ADMIN', 'CONTROLADORIA', 'CONTADOR') 
NOT NULL DEFAULT 'CONTADOR';

-- Verificar resultado
SELECT id, user_name, role, planta FROM user_table;
