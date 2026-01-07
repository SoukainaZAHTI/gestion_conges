import sqlite3

def get_connection():
    conn = sqlite3.connect("conges.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS employes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricule TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        service TEXT,
        solde_conges INTEGER NOT NULL
    )
    """)



    cur.execute("""
    CREATE TABLE IF NOT EXISTS demandes_conge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employe_id INTEGER NOT NULL,
        date_debut TEXT NOT NULL,
        date_fin TEXT NOT NULL,
        type_conge TEXT NOT NULL,
        statut TEXT NOT NULL,
        commentaire TEXT,
        FOREIGN KEY (employe_id) REFERENCES employes(id)
    )
    """)

    cur.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    login
                    TEXT
                    UNIQUE
                    NOT
                    NULL,
                    mot_de_passe
                    TEXT
                    NOT
                    NULL,
                    role
                    TEXT
                    NOT
                    NULL
                )
                """)

    conn.commit()
    conn.close()
