import sqlite3

DATABASE_NAME = "database.db"


def get_db_connection():
    """Abre uma conexão simples com o banco SQLite."""
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Cria as tabelas iniciais se elas ainda não existirem."""
    connection = get_db_connection()
    connection.executescript(
        """
-- ============================================================
-- SCHEMA SQLITE3
-- Sistema de Acomodações
-- Compatível com Python sqlite3 / executescript()
-- ============================================================

PRAGMA foreign_keys = OFF;


-- ============================================================
-- LIMPEZA
-- ============================================================

-- DROP TABLE IF EXISTS reserva_atividade;
-- DROP TABLE IF EXISTS avaliacao_hospede;
-- DROP TABLE IF EXISTS avaliacao;
-- DROP TABLE IF EXISTS ocorrencia_hospede;
-- DROP TABLE IF EXISTS tipo_ocorrencia_hospede;
-- DROP TABLE IF EXISTS status_hospede;
-- DROP TABLE IF EXISTS historico_preco;
-- DROP TABLE IF EXISTS regra_desconto;
-- DROP TABLE IF EXISTS acomodacao_caracteristica;
-- DROP TABLE IF EXISTS caracteristica_acomodacao;
-- DROP TABLE IF EXISTS demanda_acomodacao;
-- DROP TABLE IF EXISTS nivel_demanda;
-- DROP TABLE IF EXISTS regra_estacao_atividade;
-- DROP TABLE IF EXISTS regra_feriado;
-- DROP TABLE IF EXISTS feriado;
-- DROP TABLE IF EXISTS regra_dia_semana;
-- DROP TABLE IF EXISTS regra_estacao;
-- DROP TABLE IF EXISTS estacao;
-- DROP TABLE IF EXISTS acomodacao_atividade;
-- DROP TABLE IF EXISTS acomodacao_comodidade;
-- DROP TABLE IF EXISTS comodidade;
-- DROP TABLE IF EXISTS foto;
-- DROP TABLE IF EXISTS reserva;
-- DROP TABLE IF EXISTS acomodacao;
-- DROP TABLE IF EXISTS endereco;
-- DROP TABLE IF EXISTS atividade;
-- DROP TABLE IF EXISTS anfitriao;
-- DROP TABLE IF EXISTS usuario;

-- ============================================================
-- 1. USUARIO
-- ============================================================

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    data_nascimento DATE,

    data_cadastro DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    ativo INTEGER NOT NULL DEFAULT 1,

    CHECK (ativo IN (0, 1)),
    CHECK (length(trim(email)) > 0)
);


CREATE INDEX idx_usuario_nome
ON usuario(nome);

CREATE INDEX idx_usuario_ativo
ON usuario(ativo);


-- ============================================================
-- 2. ANFITRIAO
-- Relacionamento:
-- usuario 1 ---- 0..1 anfitriao
-- ============================================================

CREATE TABLE IF NOT EXISTS anfitriao (
    id_anfitriao INTEGER PRIMARY KEY AUTOINCREMENT,

    id_usuario INTEGER NOT NULL UNIQUE,

    descricao VARCHAR(500),

    data_inicio DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_anfitriao_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 3. ENDERECO
-- Um endereço pode ser compartilhado por várias acomodações.
-- ============================================================

CREATE TABLE IF NOT EXISTS endereco (
    id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,

    cep VARCHAR(10) NOT NULL,
    logradouro VARCHAR(150) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    complemento VARCHAR(100),
    bairro VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(100) NOT NULL,

    pais VARCHAR(100) NOT NULL
        DEFAULT 'Brasil',

    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),

    CHECK (
        latitude IS NULL
        OR latitude BETWEEN -90 AND 90
    ),

    CHECK (
        longitude IS NULL
        OR longitude BETWEEN -180 AND 180
    )
);


CREATE INDEX idx_endereco_cep
ON endereco(cep);


-- ============================================================
-- 4. ATIVIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS atividade (
    id_atividade INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(150) NOT NULL,
    descricao TEXT,

    duracao_minutos INTEGER,

    preco DECIMAL(10,2) NOT NULL
        DEFAULT 0.00,

    CHECK (
        duracao_minutos IS NULL
        OR duracao_minutos > 0
    ),

    CHECK (preco >= 0)
);


CREATE INDEX idx_atividade_nome
ON atividade(nome);


-- ============================================================
-- 5. ACOMODACAO
-- ============================================================

CREATE TABLE IF NOT EXISTS acomodacao (
    id_acomodacao INTEGER PRIMARY KEY AUTOINCREMENT,

    id_anfitriao INTEGER NOT NULL,
    id_endereco INTEGER NOT NULL,

    titulo VARCHAR(150) NOT NULL,
    descricao TEXT,

    tipo VARCHAR(50) NOT NULL,

    area_m2 DECIMAL(10,2) NOT NULL,

    capacidade INTEGER NOT NULL,

    qtd_quartos INTEGER NOT NULL
        DEFAULT 1,

    qtd_banheiros INTEGER NOT NULL
        DEFAULT 1,

    aceita_pet INTEGER NOT NULL
        DEFAULT 0,

    taxa_pet DECIMAL(10,2) NOT NULL
        DEFAULT 0.00,

    preco_noite DECIMAL(10,2) NOT NULL,

    status VARCHAR(30) NOT NULL
        DEFAULT 'DISPONIVEL',

    data_cadastro DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_acomodacao_anfitriao
        FOREIGN KEY (id_anfitriao)
        REFERENCES anfitriao(id_anfitriao)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_acomodacao_endereco
        FOREIGN KEY (id_endereco)
        REFERENCES endereco(id_endereco)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (area_m2 > 0),
    CHECK (capacidade > 0),
    CHECK (qtd_quartos >= 0),
    CHECK (qtd_banheiros >= 0),
    CHECK (aceita_pet IN (0, 1)),
    CHECK (taxa_pet >= 0),
    CHECK (preco_noite >= 0)
);


CREATE INDEX idx_acomodacao_anfitriao
ON acomodacao(id_anfitriao);

CREATE INDEX idx_acomodacao_endereco
ON acomodacao(id_endereco);

CREATE INDEX idx_acomodacao_tipo
ON acomodacao(tipo);

CREATE INDEX idx_acomodacao_status
ON acomodacao(status);


-- ============================================================
-- 6. FOTO
-- ============================================================

CREATE TABLE IF NOT EXISTS foto (
    id_foto INTEGER PRIMARY KEY AUTOINCREMENT,

    id_acomodacao INTEGER NOT NULL,

    url VARCHAR(500) NOT NULL,
    descricao VARCHAR(200),

    ordem INTEGER NOT NULL
        DEFAULT 1,

    CONSTRAINT fk_foto_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (ordem >= 1)
);


CREATE INDEX idx_foto_acomodacao
ON foto(id_acomodacao);


-- ============================================================
-- 7. COMODIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS comodidade (
    id_comodidade INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(300)
);


-- ============================================================
-- 8. ACOMODACAO_COMODIDADE
-- Relacionamento N:N
-- ============================================================

CREATE TABLE IF NOT EXISTS acomodacao_comodidade (
    id_acomodacao INTEGER NOT NULL,
    id_comodidade INTEGER NOT NULL,

    PRIMARY KEY (
        id_acomodacao,
        id_comodidade
    ),

    CONSTRAINT fk_acomodacao_comodidade_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_acomodacao_comodidade_comodidade
        FOREIGN KEY (id_comodidade)
        REFERENCES comodidade(id_comodidade)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 9. ACOMODACAO_ATIVIDADE
-- Relacionamento N:N
-- ============================================================

CREATE TABLE IF NOT EXISTS acomodacao_atividade (
    id_acomodacao INTEGER NOT NULL,
    id_atividade INTEGER NOT NULL,

    PRIMARY KEY (
        id_acomodacao,
        id_atividade
    ),

    CONSTRAINT fk_acomodacao_atividade_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_acomodacao_atividade_atividade
        FOREIGN KEY (id_atividade)
        REFERENCES atividade(id_atividade)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- ============================================================
-- 10. RESERVA
-- ============================================================

CREATE TABLE IF NOT EXISTS reserva (
    id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,

    id_acomodacao INTEGER NOT NULL,
    id_hospede INTEGER NOT NULL,

    check_in DATE NOT NULL,
    check_out DATE NOT NULL,

    quantidade_hospedes INTEGER NOT NULL,

    valor_total DECIMAL(10,2) NOT NULL,

    status VARCHAR(30) NOT NULL
        DEFAULT 'PENDENTE',

    data_reserva DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    -- Necessário para FK composta de reserva_atividade
    UNIQUE (
        id_reserva,
        id_acomodacao
    ),

    CONSTRAINT fk_reserva_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_reserva_hospede
        FOREIGN KEY (id_hospede)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (check_out > check_in),

    CHECK (quantidade_hospedes > 0),

    CHECK (valor_total >= 0)
);


CREATE INDEX idx_reserva_acomodacao
ON reserva(id_acomodacao);

CREATE INDEX idx_reserva_hospede
ON reserva(id_hospede);

CREATE INDEX idx_reserva_datas
ON reserva(
    id_acomodacao,
    check_in,
    check_out
);

CREATE INDEX idx_reserva_status
ON reserva(status);


-- ============================================================
-- 11. RESERVA_ATIVIDADE
--
-- A FK composta garante:
--
-- reserva -> acomodacao
--
-- e
--
-- acomodacao -> atividade
--
-- evitando adicionar uma atividade que não pertence
-- à acomodação reservada.
-- ============================================================

CREATE TABLE IF NOT EXISTS reserva_atividade (
    id_reserva INTEGER NOT NULL,
    id_acomodacao INTEGER NOT NULL,
    id_atividade INTEGER NOT NULL,

    quantidade INTEGER NOT NULL
        DEFAULT 1,

    valor_unitario DECIMAL(10,2) NOT NULL,

    PRIMARY KEY (
        id_reserva,
        id_atividade
    ),

    CONSTRAINT fk_reserva_atividade_reserva_acomodacao
        FOREIGN KEY (
            id_reserva,
            id_acomodacao
        )
        REFERENCES reserva(
            id_reserva,
            id_acomodacao
        )
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_reserva_atividade_acomodacao_atividade
        FOREIGN KEY (
            id_acomodacao,
            id_atividade
        )
        REFERENCES acomodacao_atividade(
            id_acomodacao,
            id_atividade
        )
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (quantidade > 0),

    CHECK (valor_unitario >= 0)
);


CREATE INDEX idx_reserva_atividade_acomodacao
ON reserva_atividade(
    id_acomodacao,
    id_atividade
);


-- ============================================================
-- 12. AVALIACAO
-- Uma reserva pode ter no máximo uma avaliação.
-- ============================================================

CREATE TABLE IF NOT EXISTS avaliacao (
    id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,

    id_reserva INTEGER NOT NULL UNIQUE,

    nota INTEGER NOT NULL,

    comentario TEXT,

    nota_localizacao INTEGER,
    nota_limpeza INTEGER,
    nota_comunicacao INTEGER,
    nota_checkin INTEGER,

    data_avaliacao DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_avaliacao_reserva
        FOREIGN KEY (id_reserva)
        REFERENCES reserva(id_reserva)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (nota BETWEEN 1 AND 5),

    CHECK (
        nota_localizacao IS NULL
        OR nota_localizacao BETWEEN 1 AND 5
    ),

    CHECK (
        nota_limpeza IS NULL
        OR nota_limpeza BETWEEN 1 AND 5
    ),

    CHECK (
        nota_comunicacao IS NULL
        OR nota_comunicacao BETWEEN 1 AND 5
    ),

    CHECK (
        nota_checkin IS NULL
        OR nota_checkin BETWEEN 1 AND 5
    )
);


-- ============================================================
-- 13. ESTACAO
-- ============================================================

CREATE TABLE IF NOT EXISTS estacao (
    id_estacao INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(30) NOT NULL UNIQUE,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    descricao VARCHAR(300),

    CHECK (percentual_ajuste >= -100)
);


-- ============================================================
-- 14. REGRA_ESTACAO
-- ============================================================

CREATE TABLE IF NOT EXISTS regra_estacao (
    id_regra_estacao INTEGER PRIMARY KEY AUTOINCREMENT,

    id_estacao INTEGER NOT NULL,

    tipo_acomodacao VARCHAR(50),

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    descricao VARCHAR(300),

    CONSTRAINT fk_regra_estacao_estacao
        FOREIGN KEY (id_estacao)
        REFERENCES estacao(id_estacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


CREATE INDEX idx_regra_estacao_estacao
ON regra_estacao(id_estacao);

CREATE INDEX idx_regra_estacao_tipo
ON regra_estacao(tipo_acomodacao);


-- ============================================================
-- 15. FERIADO
-- ============================================================

CREATE TABLE IF NOT EXISTS feriado (
    id_feriado INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(100) NOT NULL,

    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    descricao VARCHAR(300),

    CHECK (data_fim >= data_inicio)
);


CREATE INDEX idx_feriado_datas
ON feriado(data_inicio, data_fim);


-- ============================================================
-- 16. REGRA_FERIADO
-- ============================================================

CREATE TABLE IF NOT EXISTS regra_feriado (
    id_regra_feriado INTEGER PRIMARY KEY AUTOINCREMENT,

    id_feriado INTEGER NOT NULL,

    -- NULL = regra geral
    -- preenchido = regra específica
    id_acomodacao INTEGER,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    descricao VARCHAR(300),

    CONSTRAINT fk_regra_feriado_feriado
        FOREIGN KEY (id_feriado)
        REFERENCES feriado(id_feriado)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_regra_feriado_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


CREATE INDEX idx_regra_feriado_feriado
ON regra_feriado(id_feriado);

CREATE INDEX idx_regra_feriado_acomodacao
ON regra_feriado(id_acomodacao);


-- ============================================================
-- 17. REGRA_DIA_SEMANA
-- 1 = Domingo
-- 2 = Segunda
-- 3 = Terça
-- 4 = Quarta
-- 5 = Quinta
-- 6 = Sexta
-- 7 = Sábado
-- ============================================================

CREATE TABLE IF NOT EXISTS regra_dia_semana (
    id_regra_dia INTEGER PRIMARY KEY AUTOINCREMENT,

    dia_semana INTEGER NOT NULL,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    descricao VARCHAR(200),

    CHECK (dia_semana BETWEEN 1 AND 7)
);


-- ============================================================
-- 18. NIVEL_DEMANDA
-- ============================================================

CREATE TABLE IF NOT EXISTS nivel_demanda (
    id_nivel_demanda INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(30) NOT NULL UNIQUE,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    descricao VARCHAR(300)
);


-- ============================================================
-- 19. DEMANDA_ACOMODACAO
-- ============================================================

CREATE TABLE IF NOT EXISTS demanda_acomodacao (
    id_demanda INTEGER PRIMARY KEY AUTOINCREMENT,

    id_acomodacao INTEGER NOT NULL,
    id_nivel_demanda INTEGER NOT NULL,

    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    quantidade_visualizacoes INTEGER NOT NULL
        DEFAULT 0,

    quantidade_reservas INTEGER NOT NULL
        DEFAULT 0,

    CONSTRAINT fk_demanda_acomodacao_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_demanda_acomodacao_nivel
        FOREIGN KEY (id_nivel_demanda)
        REFERENCES nivel_demanda(id_nivel_demanda)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (data_fim >= data_inicio),

    CHECK (quantidade_visualizacoes >= 0),

    CHECK (quantidade_reservas >= 0)
);


CREATE INDEX idx_demanda_acomodacao
ON demanda_acomodacao(id_acomodacao);

CREATE INDEX idx_demanda_nivel
ON demanda_acomodacao(id_nivel_demanda);

CREATE INDEX idx_demanda_datas
ON demanda_acomodacao(
    id_acomodacao,
    data_inicio,
    data_fim
);


-- ============================================================
-- 20. CARACTERISTICA_ACOMODACAO
-- ============================================================

CREATE TABLE IF NOT EXISTS caracteristica_acomodacao (
    id_caracteristica INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(100) NOT NULL UNIQUE,

    categoria VARCHAR(50),

    descricao VARCHAR(300)
);


-- ============================================================
-- 21. ACOMODACAO_CARACTERISTICA
-- ============================================================

CREATE TABLE IF NOT EXISTS acomodacao_caracteristica (
    id_acomodacao INTEGER NOT NULL,
    id_caracteristica INTEGER NOT NULL,

    quantidade INTEGER NOT NULL
        DEFAULT 1,

    influencia_preco INTEGER NOT NULL
        DEFAULT 0,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    PRIMARY KEY (
        id_acomodacao,
        id_caracteristica
    ),

    CONSTRAINT fk_acomodacao_caracteristica_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_acomodacao_caracteristica_caracteristica
        FOREIGN KEY (id_caracteristica)
        REFERENCES caracteristica_acomodacao(id_caracteristica)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (quantidade > 0),

    CHECK (influencia_preco IN (0, 1))
);


-- ============================================================
-- 22. REGRA_DESCONTO
-- ============================================================

CREATE TABLE IF NOT EXISTS regra_desconto (
    id_regra_desconto INTEGER PRIMARY KEY AUTOINCREMENT,

    id_acomodacao INTEGER NOT NULL,

    quantidade_minima_dias INTEGER NOT NULL,

    percentual_desconto DECIMAL(5,2) NOT NULL,

    descricao VARCHAR(300),

    CONSTRAINT fk_regra_desconto_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (quantidade_minima_dias > 0),

    CHECK (
        percentual_desconto BETWEEN 0 AND 100
    )
);


CREATE INDEX idx_regra_desconto_acomodacao
ON regra_desconto(id_acomodacao);


-- ============================================================
-- 23. HISTORICO_PRECO
-- ============================================================

CREATE TABLE IF NOT EXISTS historico_preco (
    id_historico_preco INTEGER PRIMARY KEY AUTOINCREMENT,

    id_acomodacao INTEGER NOT NULL,

    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,

    preco_base DECIMAL(10,2) NOT NULL,

    percentual_estacao DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    percentual_demanda DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    percentual_fim_semana DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    percentual_feriado DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    percentual_caracteristicas DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    percentual_hospedes DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    percentual_desconto DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    preco_final DECIMAL(10,2) NOT NULL,

    motivo VARCHAR(500),

    data_calculo DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_historico_preco_acomodacao
        FOREIGN KEY (id_acomodacao)
        REFERENCES acomodacao(id_acomodacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (data_fim >= data_inicio),

    CHECK (preco_base >= 0),

    CHECK (preco_final >= 0)
);


CREATE INDEX idx_historico_preco_acomodacao
ON historico_preco(id_acomodacao);

CREATE INDEX idx_historico_preco_datas
ON historico_preco(
    id_acomodacao,
    data_inicio,
    data_fim
);


-- ============================================================
-- 24. REGRA_ESTACAO_ATIVIDADE
-- ============================================================

CREATE TABLE IF NOT EXISTS regra_estacao_atividade (
    id_regra INTEGER PRIMARY KEY AUTOINCREMENT,

    id_atividade INTEGER NOT NULL,
    id_estacao INTEGER NOT NULL,

    percentual_ajuste DECIMAL(5,2) NOT NULL
        DEFAULT 0.00,

    procura VARCHAR(30),

    descricao VARCHAR(300),

    CONSTRAINT fk_regra_estacao_atividade_atividade
        FOREIGN KEY (id_atividade)
        REFERENCES atividade(id_atividade)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_regra_estacao_atividade_estacao
        FOREIGN KEY (id_estacao)
        REFERENCES estacao(id_estacao)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


CREATE INDEX idx_regra_estacao_atividade_atividade
ON regra_estacao_atividade(id_atividade);

CREATE INDEX idx_regra_estacao_atividade_estacao
ON regra_estacao_atividade(id_estacao);


-- ============================================================
-- 25. AVALIACAO_HOSPEDE
-- ============================================================

CREATE TABLE IF NOT EXISTS avaliacao_hospede (
    id_avaliacao_hospede INTEGER PRIMARY KEY AUTOINCREMENT,

    id_reserva INTEGER NOT NULL UNIQUE,

    nota_geral INTEGER NOT NULL,

    deixou_organizado INTEGER,
    deixou_lixo INTEGER,
    respeitou_regras INTEGER,
    comunicacao_adequada INTEGER,

    comentario TEXT,

    data_avaliacao DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_avaliacao_hospede_reserva
        FOREIGN KEY (id_reserva)
        REFERENCES reserva(id_reserva)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (nota_geral BETWEEN 1 AND 5),

    CHECK (
        deixou_organizado IS NULL
        OR deixou_organizado IN (0, 1)
    ),

    CHECK (
        deixou_lixo IS NULL
        OR deixou_lixo IN (0, 1)
    ),

    CHECK (
        respeitou_regras IS NULL
        OR respeitou_regras IN (0, 1)
    ),

    CHECK (
        comunicacao_adequada IS NULL
        OR comunicacao_adequada IN (0, 1)
    )
);


-- ============================================================
-- 26. TIPO_OCORRENCIA_HOSPEDE
-- ============================================================

CREATE TABLE IF NOT EXISTS tipo_ocorrencia_hospede (
    id_tipo_ocorrencia INTEGER PRIMARY KEY AUTOINCREMENT,

    nome VARCHAR(100) NOT NULL UNIQUE,

    gravidade VARCHAR(30) NOT NULL,

    descricao VARCHAR(300)
);


-- ============================================================
-- 27. OCORRENCIA_HOSPEDE
-- ============================================================

CREATE TABLE IF NOT EXISTS ocorrencia_hospede (
    id_ocorrencia INTEGER PRIMARY KEY AUTOINCREMENT,

    id_reserva INTEGER NOT NULL,
    id_tipo_ocorrencia INTEGER NOT NULL,

    descricao TEXT NOT NULL,

    gravidade VARCHAR(30) NOT NULL,

    valor_prejuizo DECIMAL(10,2),

    data_ocorrencia DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    resolvida INTEGER NOT NULL
        DEFAULT 0,

    CONSTRAINT fk_ocorrencia_reserva
        FOREIGN KEY (id_reserva)
        REFERENCES reserva(id_reserva)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_ocorrencia_tipo
        FOREIGN KEY (id_tipo_ocorrencia)
        REFERENCES tipo_ocorrencia_hospede(id_tipo_ocorrencia)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (
        valor_prejuizo IS NULL
        OR valor_prejuizo >= 0
    ),

    CHECK (resolvida IN (0, 1))
);


CREATE INDEX idx_ocorrencia_reserva
ON ocorrencia_hospede(id_reserva);

CREATE INDEX idx_ocorrencia_tipo
ON ocorrencia_hospede(id_tipo_ocorrencia);


-- ============================================================
-- 28. STATUS_HOSPEDE
--
-- Relacionamento:
--
-- usuario 1 ---- N status_hospede
--
-- Permite histórico de status.
-- ============================================================

CREATE TABLE IF NOT EXISTS status_hospede (
    id_status_hospede INTEGER PRIMARY KEY AUTOINCREMENT,

    id_usuario INTEGER NOT NULL,

    status VARCHAR(30) NOT NULL
        DEFAULT 'ATIVO',

    motivo VARCHAR(500),

    data_inicio DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    data_fim DATETIME,

    CONSTRAINT fk_status_hospede_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CHECK (
        data_fim IS NULL
        OR data_fim >= data_inicio
    )
);


CREATE INDEX idx_status_hospede_usuario
ON status_hospede(id_usuario);

CREATE INDEX idx_status_hospede_periodo
ON status_hospede(
    id_usuario,
    data_inicio,
    data_fim
);


-- ============================================================
-- ATIVA AS FOREIGN KEYS
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- FIM
-- ============================================================

        """
    )
    connection.commit()
    connection.close()
