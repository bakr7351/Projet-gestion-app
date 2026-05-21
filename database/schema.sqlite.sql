-- Schéma SQLite — Application Absorption / Désorption
-- Compatible avec les modèles SQLAlchemy (backend/models/)
-- Usage : sqlite3 database/absorption.db < database/schema.sqlite.sql

PRAGMA foreign_keys = ON;

-- Utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    statut VARCHAR(20) NOT NULL DEFAULT 'non_verifie'
        CHECK (statut IN ('non_verifie', 'actif', 'desactive', 'banni')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    ip_inscription VARCHAR(45),
    promoted_by INTEGER REFERENCES users(id),
    api_access_enabled BOOLEAN DEFAULT 0,
    api_rate_limit INTEGER DEFAULT 1000,
    last_api_access DATETIME,
    derniere_connexion DATETIME
);

-- Tokens (vérification email, reset mot de passe)
CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(30) NOT NULL CHECK (type IN ('email_verification', 'password_reset')),
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Historique des calculs
CREATE TABLE IF NOT EXISTS calculation_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    calculation_type VARCHAR(20) NOT NULL
        CHECK (calculation_type IN ('absorption', 'desorption', 'mccabe_thiele')),
    custom_name VARCHAR(100),
    input_parameters TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_calculation_history_user_created
    ON calculation_history (user_id, created_at);

-- Journal d'audit admin
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(100) NOT NULL,
    target_id INTEGER NOT NULL REFERENCES users(id),
    author_id INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- Historique connexions
CREATE TABLE IF NOT EXISTS login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 1
);

-- Tentatives de connexion / blocage
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier VARCHAR(255) NOT NULL,
    identifier_type VARCHAR(20) NOT NULL CHECK (identifier_type IN ('email', 'ip')),
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    blocked_until DATETIME,
    last_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
    block_level INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_login_attempts_identifier
    ON login_attempts (identifier, identifier_type);

-- Surveillance IP
CREATE TABLE IF NOT EXISTS ip_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(45) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(10) NOT NULL CHECK (event_type IN ('signup', 'login')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS banned_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    banned_by INTEGER NOT NULL REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Utilisateurs archivés (suppression)
CREATE TABLE IF NOT EXISTS archived_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_id INTEGER NOT NULL,
    data_snapshot TEXT NOT NULL,
    deleted_by INTEGER NOT NULL REFERENCES users(id),
    deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
