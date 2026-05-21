-- ============================================
-- 🗄️ SQL Server Setup Script for CyberShield-AI
-- ============================================
-- Exécuter cette script dans SQL Server Management Studio (SSMS)
-- sur votre Windows Server 2019/2022

-- Créer la base de données
CREATE DATABASE CyberShield_AI;
GO

USE CyberShield_AI;
GO

-- ========== TABLE: Détections ==========
CREATE TABLE detections (
    id INT PRIMARY KEY IDENTITY(1,1),
    timestamp DATETIME DEFAULT GETDATE(),
    threat_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    duration_connexion INT,
    nb_connexions_par_sec INT,
    volume_donnees_kb INT,
    nb_erreurs INT,
    nb_ports_scanes INT,
    taux_echec_connexion FLOAT,
    taille_paquets_moy INT,
    nb_tentatives_auth INT,
    remediation_action VARCHAR(500),
    status VARCHAR(20) DEFAULT 'detected',
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- ========== TABLE: Logs Système ==========
CREATE TABLE system_logs (
    id INT PRIMARY KEY IDENTITY(1,1),
    timestamp DATETIME DEFAULT GETDATE(),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20),
    message VARCHAR(MAX),
    user_id INT,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT GETDATE()
);

-- ========== TABLE: Statistiques ==========
CREATE TABLE statistics (
    id INT PRIMARY KEY IDENTITY(1,1),
    date_stat DATE DEFAULT CAST(GETDATE() AS DATE),
    total_detections INT DEFAULT 0,
    ddos_count INT DEFAULT 0,
    intrusion_count INT DEFAULT 0,
    malware_count INT DEFAULT 0,
    phishing_count INT DEFAULT 0,
    sql_injection_count INT DEFAULT 0,
    normal_count INT DEFAULT 0,
    avg_confidence FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE()
);

-- ========== TABLE: Configuration ==========
CREATE TABLE configuration (
    id INT PRIMARY KEY IDENTITY(1,1),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value VARCHAR(MAX),
    description VARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- ========== INDEX pour Performance ==========
CREATE INDEX idx_detections_timestamp ON detections(timestamp DESC);
CREATE INDEX idx_detections_threat_type ON detections(threat_type);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp DESC);
CREATE INDEX idx_statistics_date ON statistics(date_stat DESC);

-- ========== VIEWS pour Reporting ==========
CREATE VIEW vw_recent_detections AS
SELECT TOP 100
    id,
    timestamp,
    threat_type,
    confidence,
    remediation_action,
    status
FROM detections
ORDER BY timestamp DESC;

GO

CREATE VIEW vw_threat_summary AS
SELECT
    threat_type,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence,
    MAX(timestamp) as last_detection
FROM detections
WHERE timestamp >= DATEADD(DAY, -7, GETDATE())
GROUP BY threat_type;

GO

-- ========== STORED PROCEDURES ==========
CREATE PROCEDURE sp_insert_detection
    @threat_type VARCHAR(50),
    @confidence FLOAT,
    @duration_connexion INT = NULL,
    @nb_connexions_par_sec INT = NULL,
    @volume_donnees_kb INT = NULL,
    @nb_erreurs INT = NULL,
    @nb_ports_scanes INT = NULL,
    @taux_echec_connexion FLOAT = NULL,
    @taille_paquets_moy INT = NULL,
    @nb_tentatives_auth INT = NULL,
    @remediation_action VARCHAR(500) = NULL
AS
BEGIN
    INSERT INTO detections (
        threat_type,
        confidence,
        duration_connexion,
        nb_connexions_par_sec,
        volume_donnees_kb,
        nb_erreurs,
        nb_ports_scanes,
        taux_echec_connexion,
        taille_paquets_moy,
        nb_tentatives_auth,
        remediation_action
    ) VALUES (
        @threat_type,
        @confidence,
        @duration_connexion,
        @nb_connexions_par_sec,
        @volume_donnees_kb,
        @nb_erreurs,
        @nb_ports_scanes,
        @taux_echec_connexion,
        @taille_paquets_moy,
        @nb_tentatives_auth,
        @remediation_action
    );
    
    SELECT @@IDENTITY as detection_id;
END;

GO

-- ========== Insertion de données de test ==========
INSERT INTO configuration (config_key, config_value, description)
VALUES 
    ('app_version', '1.0.0', 'Version de l''application'),
    ('db_version', '1.0', 'Version du schéma de base de données'),
    ('last_model_update', CAST(GETDATE() AS VARCHAR), 'Dernière mise à jour du modèle IA');

GO

-- ========== Permissions pour SQL Server Agent (si besoin) ==========
-- GRANT EXECUTE ON sp_insert_detection TO [NT AUTHORITY\SYSTEM];

-- Afficher les tables créées
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo';
