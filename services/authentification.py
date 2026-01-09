"""
Service d'authentification
Responsabilité: Logique métier liée à l'authentification et la gestion des utilisateurs
"""
from services.dao import UtilisateurDAO


class ServiceAuthentification:
    """
    Service applicatif pour l'authentification
    Responsabilités:
    - Orchestrer les opérations d'authentification
    - Valider les règles métier (ex: rôles valides)
    - Coordonner l'accès aux données via UtilisateurDAO
    """

    ROLES_VALIDES = ['Employe', 'RH']

    def creer_utilisateur(self, login, mot_de_passe, role="Employe"):
        """
        Crée un nouvel utilisateur dans le système
        role par défaut: 'Employe'
        role peut être: 'RH' ou 'Employe'
        """
        # Validation métier
        if role not in self.ROLES_VALIDES:
            print(f"❌ Rôle invalide. Rôles acceptés: {', '.join(self.ROLES_VALIDES)}")
            return False

        if not login or not mot_de_passe:
            print("❌ Login et mot de passe requis")
            return False

        # ✅ Délégation au DAO (plus de SQL direct!)
        try:
            user_id = UtilisateurDAO.creer(login, mot_de_passe, role)
            print(f"✅ Compte créé avec succès (Rôle: {role}, ID: {user_id})")
            return True
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                print("❌ Erreur: Ce login existe déjà")
            else:
                print(f"❌ Erreur lors de la création: {e}")
            return False

    def authentifier(self, login, mot_de_passe):
        """
        Authentifie un utilisateur et retourne l'objet Utilisateur si succès
        Retourne None si échec
        """
        if not login or not mot_de_passe:
            print("❌ Login et mot de passe requis")
            return None

        try:
            # ✅ Utilise le DAO
            utilisateur = UtilisateurDAO.authentifier(login, mot_de_passe)

            if utilisateur:
                print(f"✅ Authentification réussie - Bienvenue {utilisateur.login} ({utilisateur.role})")
            else:
                print("❌ Login ou mot de passe incorrect")

            return utilisateur

        except Exception as e:
            print(f"❌ Erreur d'authentification: {e}")
            return None

    def lister_utilisateurs(self):
        """Liste tous les utilisateurs (pour administration)"""
        try:
            # ✅ Utilise le DAO
            utilisateurs = UtilisateurDAO.lister_tous()
            return utilisateurs
        except Exception as e:
            print(f"❌ Erreur lors de la récupération: {e}")
            return []

    def supprimer_utilisateur(self, user_id):
        """Supprime un utilisateur"""
        try:
            # ✅ Utilise le DAO
            succes = UtilisateurDAO.supprimer(user_id)
            if succes:
                print(f"✅ Utilisateur supprimé (ID: {user_id})")
            else:
                print(f"❌ Utilisateur introuvable (ID: {user_id})")
            return succes
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False

    def modifier_role(self, user_id, nouveau_role):
        """Modifie le rôle d'un utilisateur"""
        # Validation métier
        if nouveau_role not in self.ROLES_VALIDES:
            print(f"❌ Rôle invalide. Rôles acceptés: {', '.join(self.ROLES_VALIDES)}")
            return False

        try:
            # ✅ Utilise le DAO
            succes = UtilisateurDAO.modifier_role(user_id, nouveau_role)
            if succes:
                print(f"✅ Rôle modifié en '{nouveau_role}' (ID: {user_id})")
            else:
                print(f"❌ Utilisateur introuvable (ID: {user_id})")
            return succes
        except Exception as e:
            print(f"❌ Erreur lors de la modification: {e}")
            return False

    def verifier_acces_rh(self, utilisateur):
        """
        Vérifie si un utilisateur a les droits RH
        Utile pour contrôler l'accès aux fonctionnalités d'administration
        """
        if not utilisateur:
            return False
        return utilisateur.role == 'RH'

    def changer_mot_de_passe(self, user_id, ancien_mdp, nouveau_mdp):
        """
        Change le mot de passe d'un utilisateur
        Nécessite l'ancien mot de passe pour validation
        """
        if not nouveau_mdp:
            print("❌ Le nouveau mot de passe ne peut pas être vide")
            return False

        try:
            # ✅ Utilise le DAO
            utilisateur = UtilisateurDAO.trouver_par_id(user_id)

            if not utilisateur:
                print("❌ Utilisateur introuvable")
                return False

            if utilisateur.mot_de_passe != ancien_mdp:
                print("❌ Ancien mot de passe incorrect")
                return False

            # ✅ Utilise le DAO
            succes = UtilisateurDAO.modifier_mot_de_passe(user_id, nouveau_mdp)

            if succes:
                print("✅ Mot de passe modifié avec succès")
            else:
                print("❌ Erreur lors de la modification")

            return succes

        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False