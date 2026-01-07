from database import get_connection
from models.utilisateurs import Utilisateur


class ServiceAuthentification:

    def creer_utilisateur(self, login, mot_de_passe, role="Employe"):
        """
        Crée un nouvel utilisateur dans le système
        role par défaut: 'Employe'
        role peut être: 'RH' ou 'Employe'
        """
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO utilisateurs (login, mot_de_passe, role)
                        VALUES (?, ?, ?)
                        """, (login, mot_de_passe, role))
            conn.commit()
            print(f"Compte créé avec succès (Rôle: {role})")
            return True
        except sqlite3.IntegrityError:
            print("Erreur: Ce login existe déjà")
            return False
        finally:
            conn.close()
    def authentifier(self, login, mot_de_passe):
        """
        Authentifie un utilisateur et retourne l'objet Utilisateur si succès
        Retourne None si échec
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT *
                    FROM utilisateurs
                    WHERE login = ?
                      AND mot_de_passe = ?
                    """, (login, mot_de_passe))
        row = cur.fetchone()
        conn.close()

        if row:
            return Utilisateur(**row)
        return None

    def lister_utilisateurs(self):
        """Liste tous les utilisateurs (pour administration)"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM utilisateurs")
        rows = cur.fetchall()
        conn.close()
        return [Utilisateur(**row) for row in rows]

    def supprimer_utilisateur(self, user_id):
        """Supprime un utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def modifier_role(self, user_id, nouveau_role):
        """Modifie le rôle d'un utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE utilisateurs SET role = ? WHERE id = ?",
                    (nouveau_role, user_id))
        conn.commit()
        conn.close()