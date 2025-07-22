CREATE DATABASE CRYPTO_PROJECT;
GO

CREATE TABLE Project (
    ID INT PRIMARY KEY IDENTITY(1,1),
    NamaProject VARCHAR(100) NOT NULL,
    KapanMulai VARCHAR(40) NOT NULL,
    Jaringan VARCHAR(30) NOT NULL,
    Fase VARCHAR(10) NOT NULL DEFAULT 'Testnet',
    Misi VARCHAR(MAX) NULL,
    InfoTGE VARCHAR(255) NULL,
    LinkGarapan VARCHAR(500) NULL,
    KodeReferal VARCHAR(50) NULL,
    Status VARCHAR(50) NOT NULL,
    InfoListing VARCHAR(50) NULL
);
GO

INSERT INTO Project (NamaProject, KapanMulai, Jaringan, Fase, Misi, InfoTGE, LinkGarapan, KodeReferal, Status, Infolisting) VALUES
('R2', 'Maret', 'Sepolia', 'Testnet', 'Daily Swap & Faucet', 'NA', 'https://www.r2.money/dashboard', '', 'ONGOING', 'NA');
GO

SELECT * FROM Project;
