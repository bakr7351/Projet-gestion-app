-- 🔥 Supprimer et recréer la base
IF DB_ID('projet_app') IS NOT NULL
    DROP DATABASE projet_app;
GO

CREATE DATABASE projet_app;
GO

USE projet_app;
GO

-- ==============================
-- 👤 TABLE USERS
-- ==============================
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(100) NOT NULL,
    last_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(10) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    status NVARCHAR(20) DEFAULT 'non_verifie' 
        CHECK (status IN ('non_verifie', 'actif', 'desactive', 'banni')),
    ip_address NVARCHAR(45),
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- ==============================
-- 🧪 TABLE CALCULATIONS
-- ==============================
CREATE TABLE calculations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    type NVARCHAR(20) CHECK (type IN ('absorption', 'desorption')),
    input_data NVARCHAR(MAX),
    result FLOAT,
    is_archived BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_calc_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);
GO

-- ==============================
-- 📜 TABLE HISTORY
-- ==============================
CREATE TABLE history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    action NVARCHAR(255),
    description NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_history_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE SET NULL
);
GO

-- ==============================
-- 🌐 TABLE IP LOGS
-- ==============================
CREATE TABLE ip_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    ip_address NVARCHAR(45),
    action NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_ip_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE SET NULL
);
GO

-- ==============================
-- 📧 TABLE EMAIL VERIFICATION
-- ==============================
CREATE TABLE email_verification (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT UNIQUE,
    token NVARCHAR(255),
    expires_at DATETIME,
    verified BIT DEFAULT 0,

    CONSTRAINT FK_email_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);
GO

-- ==============================
-- 🔐 TABLE PASSWORD RESETS
-- ==============================
CREATE TABLE password_resets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    token NVARCHAR(255),
    expires_at DATETIME,

    CONSTRAINT FK_reset_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);
GO

-- ==============================
-- 🗂️ TABLE ARCHIVE
-- ==============================
CREATE TABLE archive (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT,
    data NVARCHAR(MAX),
    type NVARCHAR(50),
    archived_at DATETIME DEFAULT GETDATE()
);
GO

-- ==============================
-- ⚡ INDEX
-- ==============================
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_calc_user ON calculations(user_id);
CREATE INDEX idx_history_user ON history(user_id);
CREATE INDEX idx_ip_user ON ip_logs(user_id);
GO