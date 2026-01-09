"""
Data Access Object (DAO) Layer
Sépare la logique d'accès aux données de la logique métier
"""
from database import get_connection
from models.employe import Employe
from models.utilisateurs import Utilisateur


class EmployeDAO:
    """
    Couche d'accès aux données pour les employés
    Responsabilité: Toutes les opérations CRUD sur la table employes
    """

    @staticmethod
    def creer(matricule, nom, prenom, service, solde_conges):
        """Insère un nouvel employé dans la base"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO employes (matricule, nom, prenom, service, solde_conges)
                        VALUES (?, ?, ?, ?, ?)
                        """, (matricule, nom, prenom, service, solde_conges))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def trouver_par_id(employe_id):
        """Récupère un employé par son ID"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM employes WHERE id = ?", (employe_id,))
            row = cur.fetchone()
            return Employe(**row) if row else None
        finally:
            conn.close()

    @staticmethod
    def trouver_par_matricule(matricule):
        """Récupère un employé par son matricule"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM employes WHERE matricule = ?", (matricule,))
            row = cur.fetchone()
            return Employe(**row) if row else None
        finally:
            conn.close()

    @staticmethod
    def lister_tous():
        """Liste tous les employés"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM employes ORDER BY nom, prenom")
            rows = cur.fetchall()
            return [Employe(**row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def mettre_a_jour_solde(employe_id, nouveau_solde):
        """Met à jour le solde de congés d'un employé"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE employes SET solde_conges = ? WHERE id = ?",
                (nouveau_solde, employe_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def deduire_jours(employe_id, jours):
        """Déduit des jours du solde d'un employé"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE employes SET solde_conges = solde_conges - ? WHERE id = ?",
                (jours, employe_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def supprimer(employe_id):
        """Supprime un employé"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM employes WHERE id = ?", (employe_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


class DemandeDAO:
    """
    Couche d'accès aux données pour les demandes de congé
    Responsabilité: Toutes les opérations CRUD sur la table demandes_conge
    """

    @staticmethod
    def creer(employe_id, date_debut, date_fin, type_conge, statut, commentaire=""):
        """Insère une nouvelle demande de congé"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO demandes_conge (employe_id, date_debut, date_fin, type_conge, statut, commentaire)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (employe_id, date_debut, date_fin, type_conge, statut, commentaire))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def trouver_par_id(demande_id):
        """Récupère une demande avec les infos de l'employé"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        SELECT d.*, e.nom, e.prenom, e.matricule, e.solde_conges, e.service
                        FROM demandes_conge d
                                 JOIN employes e ON d.employe_id = e.id
                        WHERE d.id = ?
                        """, (demande_id,))
            return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def lister_par_employe(employe_id):
        """Liste toutes les demandes d'un employé"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        SELECT d.*, e.nom, e.prenom, e.matricule, e.solde_conges, e.service
                        FROM demandes_conge d
                                 JOIN employes e ON d.employe_id = e.id
                        WHERE d.employe_id = ?
                        ORDER BY d.date_debut DESC
                        """, (employe_id,))
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def lister_par_statut(statut):
        """Liste toutes les demandes avec un statut donné"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        SELECT d.*, e.nom, e.prenom, e.matricule, e.solde_conges, e.service
                        FROM demandes_conge d
                                 JOIN employes e ON d.employe_id = e.id
                        WHERE d.statut = ?
                        ORDER BY d.date_debut
                        """, (statut,))
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def lister_toutes():
        """Liste toutes les demandes"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        SELECT d.*, e.nom, e.prenom, e.matricule, e.solde_conges, e.service
                        FROM demandes_conge d
                                 JOIN employes e ON d.employe_id = e.id
                        ORDER BY d.date_debut DESC
                        """)
            return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def mettre_a_jour_statut(demande_id, nouveau_statut):
        """Met à jour le statut d'une demande"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE demandes_conge SET statut = ? WHERE id = ?",
                (nouveau_statut, demande_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def supprimer(demande_id):
        """Supprime une demande"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM demandes_conge WHERE id = ?", (demande_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


class UtilisateurDAO:
    """Couche d'accès aux données pour les utilisateurs"""

    @staticmethod
    def creer(login, mot_de_passe, role):
        """Insère un nouvel utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO utilisateurs (login, mot_de_passe, role)
                        VALUES (?, ?, ?)
                        """, (login, mot_de_passe, role))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def trouver_par_login(login):
        """Récupère un utilisateur par son login"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM utilisateurs WHERE login = ?", (login,))
            row = cur.fetchone()
            return Utilisateur(**row) if row else None
        finally:
            conn.close()

    @staticmethod
    def authentifier(login, mot_de_passe):
        """Authentifie un utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT * FROM utilisateurs WHERE login = ? AND mot_de_passe = ?",
                (login, mot_de_passe)
            )
            row = cur.fetchone()
            return Utilisateur(**row) if row else None
        finally:
            conn.close()

    @staticmethod
    def trouver_par_id(user_id):
        """Récupère un utilisateur par son ID"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,))
            row = cur.fetchone()
            return Utilisateur(**row) if row else None
        finally:
            conn.close()

    @staticmethod
    def lister_tous():
        """Liste tous les utilisateurs"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM utilisateurs ORDER BY login")
            rows = cur.fetchall()
            return [Utilisateur(**row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def supprimer(user_id):
        """Supprime un utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def modifier_role(user_id, nouveau_role):
        """Modifie le rôle d'un utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE utilisateurs SET role = ? WHERE id = ?",
                (nouveau_role, user_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def modifier_mot_de_passe(user_id, nouveau_mdp):
        """Modifie le mot de passe d'un utilisateur"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE utilisateurs SET mot_de_passe = ? WHERE id = ?",
                (nouveau_mdp, user_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()