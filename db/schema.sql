-- Tabela de apostas
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    bet_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    match VARCHAR(200) NOT NULL,
    competition VARCHAR(100),
    market VARCHAR(50) NOT NULL,
    odds DECIMAL(5,2) NOT NULL,
    stake DECIMAL(10,2) NOT NULL,
    probability DECIMAL(5,4) NOT NULL,
    ev DECIMAL(6,2) NOT NULL,
    phase INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    result VARCHAR(20),
    profit DECIMAL(10,2),
    closed_at TIMESTAMP
);

-- Tabela de histórico de banca
CREATE TABLE IF NOT EXISTS bankroll_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    bankroll DECIMAL(10,2) NOT NULL,
    phase INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    change_amount DECIMAL(10,2),
    description TEXT
);

-- Tabela de estatísticas diárias
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    phase INTEGER NOT NULL,
    total_bets INTEGER DEFAULT 0,
    won INTEGER DEFAULT 0,
    lost INTEGER DEFAULT 0,
    total_staked DECIMAL(10,2) DEFAULT 0,
    total_profit DECIMAL(10,2) DEFAULT 0,
    roi DECIMAL(6,2) DEFAULT 0
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_bets_status ON bets(status);
CREATE INDEX IF NOT EXISTS idx_bets_phase ON bets(phase);
CREATE INDEX IF NOT EXISTS idx_bets_timestamp ON bets(timestamp);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);

-- Insere registro inicial de banca
INSERT INTO bankroll_history (bankroll, phase, event_type, description)
VALUES (100.00, 1, 'initial', 'Banca inicial')
ON CONFLICT DO NOTHING;