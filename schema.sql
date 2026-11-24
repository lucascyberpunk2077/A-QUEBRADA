PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS vw_reputacao_jogador;
DROP TABLE IF EXISTS AVALIACAO;
DROP TABLE IF EXISTS SOLICITACAO;
DROP TABLE IF EXISTS PELADA;
DROP TABLE IF EXISTS LOCAL;
DROP TABLE IF EXISTS USUARIO;

-- ==========================================
-- 1. TABELAS E RESTRIÇÕES (PK, FK, UNIQUE, CHECK)
-- ==========================================

CREATE TABLE USUARIO (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK(length(trim(nome)) > 0),
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    senha_hash TEXT NOT NULL,
    telefone_whatsapp TEXT,
    cidade TEXT,
    posicao_preferida TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE LOCAL (
    id_local INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK(length(trim(nome)) > 0),
    endereco TEXT NOT NULL,
    bairro TEXT,
    cidade TEXT,
    tipo TEXT CHECK(tipo IN ('Futsal', 'Society', 'Campo', 'Areia'))
);

CREATE TABLE PELADA (
    id_pelada INTEGER PRIMARY KEY AUTOINCREMENT,
    id_organizador INTEGER NOT NULL,
    id_local INTEGER NOT NULL,
    data_hora TEXT NOT NULL,
    vagas_totais INTEGER NOT NULL CHECK(vagas_totais > 0),
    valor_por_pessoa REAL NOT NULL CHECK(valor_por_pessoa >= 0),
    nivel TEXT DEFAULT 'Casual',
    descricao TEXT,
    status TEXT DEFAULT 'Aberta' CHECK(status IN ('Aberta', 'Lotada', 'Finalizada', 'Cancelada')),
    FOREIGN KEY (id_organizador) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_local) REFERENCES LOCAL(id_local) ON DELETE RESTRICT
);

CREATE TABLE SOLICITACAO (
    id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pelada INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    mensagem TEXT CHECK(mensagem IS NULL OR length(mensagem) <= 500),
    status TEXT DEFAULT 'Pendente' CHECK(status IN ('Pendente', 'Aceita', 'Recusada', 'Cancelada')),
    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_resposta DATETIME,
    compareceu INTEGER CHECK(compareceu IS NULL OR compareceu IN (0, 1)),
    UNIQUE(id_pelada, id_usuario),
    FOREIGN KEY (id_pelada) REFERENCES PELADA(id_pelada) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE
);

CREATE TABLE AVALIACAO (
    id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pelada INTEGER NOT NULL,
    id_avaliador INTEGER NOT NULL,
    id_avaliado INTEGER NOT NULL,
    nota INTEGER NOT NULL CHECK(nota >= 1 AND nota <= 5),
    comentario TEXT,
    CHECK(id_avaliador != id_avaliado),
    UNIQUE(id_pelada, id_avaliador, id_avaliado),
    FOREIGN KEY (id_pelada) REFERENCES PELADA(id_pelada) ON DELETE CASCADE,
    FOREIGN KEY (id_avaliador) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_avaliado) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE
);

-- ==========================================
-- 2. ÍNDICES DE DESEMPENHO
-- ==========================================
CREATE INDEX idx_pelada_status ON PELADA(status);
CREATE INDEX idx_pelada_local ON PELADA(id_local);
CREATE INDEX idx_solicitacao_pelada_status ON SOLICITACAO(id_pelada, status);

-- ==========================================
-- 3. TRIGGERS (REGRAS DE NEGÓCIO NO BANCO)
-- ==========================================

-- RN-01 / CT 01-02: Impedir organizador de solicitar vaga na própria pelada
CREATE TRIGGER trg_impedir_organizador_solicitar
BEFORE INSERT ON SOLICITACAO
BEGIN
    SELECT RAISE(ABORT, 'Organizador nao pode solicitar vaga na propria pelada')
    WHERE EXISTS (
        SELECT 1 FROM PELADA
        WHERE id_pelada = NEW.id_pelada AND id_organizador = NEW.id_usuario
    );
END;

-- RN-06 / RN-07 / CT 01-06 / CT 01-14: Impedir solicitação se pelada não estiver Aberta ou sem vaga
CREATE TRIGGER trg_validar_pelada_aberta_solicitacao
BEFORE INSERT ON SOLICITACAO
BEGIN
    SELECT RAISE(ABORT, 'Pelada lotada ou indisponivel')
    WHERE (
        SELECT status FROM PELADA WHERE id_pelada = NEW.id_pelada
    ) != 'Aberta'
    OR (
        SELECT COUNT(*) FROM SOLICITACAO
        WHERE id_pelada = NEW.id_pelada AND status = 'Aceita'
    ) >= (
        SELECT vagas_totais FROM PELADA WHERE id_pelada = NEW.id_pelada
    );
END;

-- RN-02 / CT 01-04 / CT 09-31: Impedir aceite além do limite de vagas
CREATE TRIGGER trg_validar_limite_vagas_aceite
BEFORE UPDATE OF status ON SOLICITACAO
WHEN NEW.status = 'Aceita' AND OLD.status != 'Aceita'
BEGIN
    SELECT RAISE(ABORT, 'Sem vagas livres para aceitar solicitacao')
    WHERE (
        SELECT COUNT(*) FROM SOLICITACAO
        WHERE id_pelada = NEW.id_pelada AND status = 'Aceita'
    ) >= (
        SELECT vagas_totais FROM PELADA WHERE id_pelada = NEW.id_pelada
    )
    OR (
        SELECT status FROM PELADA WHERE id_pelada = NEW.id_pelada
    ) IN ('Cancelada', 'Finalizada');
END;

-- RN-03 / CT 01-03: Atualizar status da pelada para Lotada automaticamente ao preencher última vaga
CREATE TRIGGER trg_atualizar_status_lotada_insert
AFTER UPDATE OF status ON SOLICITACAO
WHEN NEW.status = 'Aceita'
BEGIN
    UPDATE PELADA
    SET status = 'Lotada'
    WHERE id_pelada = NEW.id_pelada
      AND status = 'Aberta'
      AND (SELECT COUNT(*) FROM SOLICITACAO WHERE id_pelada = NEW.id_pelada AND status = 'Aceita') >= vagas_totais;
END;

-- RN-09 / CT 01-05: Liberar pelada de Lotada para Aberta se uma solicitação aceita for cancelada
CREATE TRIGGER trg_liberar_vaga_cancelamento
AFTER UPDATE OF status ON SOLICITACAO
WHEN OLD.status = 'Aceita' AND NEW.status = 'Cancelada'
BEGIN
    UPDATE PELADA
    SET status = 'Aberta'
    WHERE id_pelada = NEW.id_pelada
      AND status = 'Lotada'
      AND (SELECT COUNT(*) FROM SOLICITACAO WHERE id_pelada = NEW.id_pelada AND status = 'Aceita') < vagas_totais;
END;

-- ==========================================
-- 3.1 REPUTAÇÃO DE PRESENÇA (ANTI-FURÃO)
-- ==========================================

-- RN-10: presença só pode ser marcada para jogador aceito e depois da data do jogo
CREATE TRIGGER trg_validar_marcacao_presenca
BEFORE UPDATE OF compareceu ON SOLICITACAO
WHEN NEW.compareceu IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'Presença só pode ser marcada para jogadores aceitos.')
    WHERE NEW.status != 'Aceita';
    SELECT RAISE(ABORT, 'Presença só pode ser marcada depois da data do jogo.')
    WHERE (SELECT data_hora FROM PELADA WHERE id_pelada = NEW.id_pelada) > strftime('%Y-%m-%d %H:%M', 'now', 'localtime');
END;

-- View que calcula a reputação de cada jogador
CREATE VIEW vw_reputacao_jogador AS
SELECT
    u.id_usuario,
    COUNT(s.compareceu) AS jogos_marcados,
    COALESCE(SUM(s.compareceu), 0) AS jogos_presente,
    CAST(ROUND(100.0 * SUM(s.compareceu) / COUNT(s.compareceu)) AS INTEGER) AS percentual_presenca,
    (SELECT ROUND(AVG(a.nota), 1) FROM AVALIACAO a WHERE a.id_avaliado = u.id_usuario) AS nota_media
FROM USUARIO u
LEFT JOIN SOLICITACAO s ON s.id_usuario = u.id_usuario AND s.compareceu IS NOT NULL
GROUP BY u.id_usuario;

-- ==========================================
-- 4. MASSA DE DADOS INICIAL (SEED PARA O CYPRESS)
-- Senha padrão de todos os usuários de teste: 123456
-- ==========================================
INSERT INTO USUARIO (id_usuario, nome, email, senha_hash, telefone_whatsapp, cidade, posicao_preferida) VALUES
(1, 'Organizador U1', 'u1@peladas.com', 'scrypt:32768:8:1$placeholder$hash1', '5581999990001', 'Jaboatão dos Guararapes', 'Meia'),
(2, 'Jogador U2', 'u2@peladas.com', 'scrypt:32768:8:1$placeholder$hash2', '5581999990002', 'Jaboatão dos Guararapes', 'Atacante'),
(3, 'Jogador U3', 'u3@peladas.com', 'scrypt:32768:8:1$placeholder$hash3', '5581999990003', 'Recife', 'Goleiro');

INSERT INTO LOCAL (id_local, nome, endereco, bairro, cidade, tipo) VALUES
(1, 'Arena Boa Viagem', 'Rua dos Navegantes, 500', 'Boa Viagem', 'Recife', 'Society'),
(2, 'Quadra Piedade Sport', 'Av. Bernardo Vieira de Melo, 1200', 'Piedade', 'Jaboatão dos Guararapes', 'Futsal');

INSERT INTO PELADA (id_pelada, id_organizador, id_local, data_hora, vagas_totais, valor_por_pessoa, nivel, descricao, status) VALUES
(1, 1, 1, '2026-12-20 20:00', 2, 15.00, 'Casual', 'Pelada P1 de teste com 2 vagas organizada por U1', 'Aberta');