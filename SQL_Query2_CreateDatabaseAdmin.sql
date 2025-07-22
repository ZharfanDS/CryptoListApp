CREATE DATABASE Admin_DB;
GO

USE Admin_DB;
GO

CREATE TABLE Users (
    ID INT PRIMARY KEY IDENTITY(1,1),
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(100) NOT NULL -- Menyimpan password yang sudah dienkripsi
    );
GO

INSERT INTO Users (Username, PasswordHash)
VALUES ('admin', '$2b$12$l1NjX9muUx0EwvwXGCM5eOwm7H6lXtJ37NZsvM86PI7CTb4ydA312'); -- Password hash didapat dari registrasi_admin.py password hash ini dapat dari 12345678
GO

SELECT * FROM Users;
GO
