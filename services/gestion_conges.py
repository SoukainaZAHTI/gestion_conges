"""
Service de gestion des congés
Responsabilité: Logique métier et orchestration des opérations
"""
from models.types_conge import CongeFactory
from utils.validators import valider_periode
from services.dao import EmployeDAO, DemandeDAO


class GestionConges:
    """
    Classe de gestion centrale - Service applicatif
    Responsabilités:
    - Orchestrer les opérations métier
    - Valider les règles métier
    - Coordonner l'accès aux données via les DAO
    """

    SOLDE_INITIAL_ANNUEL = 22

    def add_employe(self, matricule, nom, prenom, service, solde=None):
        """
        Ajoute un employé
        Cette méthode appartient à GestionConges car elle orchestre une opération métier,
        pas à Employe qui est un objet de données
        """
        if solde is None:
            solde = self.SOLDE_INITIAL_ANNUEL

        try:
            employe_id = EmployeDAO.creer(matricule, nom, prenom, service, solde)
            print(f"✅ Employé ajouté avec un solde de {solde} jours (ID: {employe_id})")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout: {e}")
            return False

    def list_employes(self):
        """Liste tous les employés via le DAO"""
        try:
            return EmployeDAO.lister_tous()
        except Exception as e:
            print(f"❌ Erreur lors de la récupération: {e}")
            return []

    def ajouter_demande(self, employe_id, date_debut, date_fin, type_conge, commentaire="", **kwargs):
        """
        Ajoute une demande de congé avec validation métier
        Cette méthode ne devrait PAS être dans Employe car elle nécessite
        l'accès à la base de données et l'orchestration de plusieurs opérations
        """
        # 1. Valider les dates
        valide, message = valider_periode(date_debut, date_fin)
        if not valide:
            print(f"❌ {message}")
            return False

        # 2. Récupérer l'employé via DAO
        try:
            employe = EmployeDAO.trouver_par_id(employe_id)
        except Exception as e:
            print(f"❌ Erreur d'accès aux données: {e}")
            return False

        if not employe:
            print("❌ Employé non trouvé")
            return False

        # 3. Créer l'objet Conge avec le Factory Pattern (polymorphisme)
        try:
            conge = CongeFactory.creer_conge(
                type_conge,
                None,
                employe_id,
                date_debut,
                date_fin,
                "En attente",
                commentaire,
                **kwargs
            )
        except ValueError as e:
            print(f"❌ {e}")
            return False

        # 4. Valider la demande selon les règles métier (polymorphisme)
        valide, message = conge.valider_demande(employe.solde_conges)

        if not valide:
            print(f"❌ {message}")
            return False

        # 5. Enregistrer via DAO
        try:
            demande_id = DemandeDAO.creer(
                employe_id,
                date_debut,
                date_fin,
                conge.get_type(),
                "En attente",
                commentaire
            )
            jours = conge.calculer_jours()
            print(f"✅ Demande de {jours} jours ajoutée ({conge.get_type()}) - ID: {demande_id}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement: {e}")
            return False

    def valider_demande(self, demande_id):
        """
        Valide une demande - Exemple d'orchestration de plusieurs opérations
        """
        try:
            # 1. Récupérer la demande via DAO
            row = DemandeDAO.trouver_par_id(demande_id)

            if not row:
                print("❌ Demande introuvable")
                return False

            if row['statut'] != 'En attente':
                print(f"❌ Cette demande a déjà été {row['statut']}")
                return False

            # 2. Créer l'objet Conge (polymorphisme)
            conge = CongeFactory.creer_conge(
                row['type_conge'],
                row['id'],
                row['employe_id'],
                row['date_debut'],
                row['date_fin'],
                row['statut'],
                row['commentaire']
            )

            # 3. Valider selon les règles métier (polymorphisme)
            valide, message = conge.valider_demande(row['solde_conges'])

            if not valide:
                print(f"❌ VALIDATION IMPOSSIBLE!")
                print(f"   Employé: {row['nom']} {row['prenom']}")
                print(f"   {message}")
                return False

            # 4. Mettre à jour le statut via DAO
            DemandeDAO.mettre_a_jour_statut(demande_id, 'Validée')

            # 5. Déduire du solde si nécessaire (polymorphisme)
            if conge.deduit_du_solde():
                jours_a_deduire = conge.calculer_jours_deductibles()
                EmployeDAO.deduire_jours(row['employe_id'], jours_a_deduire)
                print(f"✅ Demande validée - {jours_a_deduire} jours déduits")
            else:
                print(f"✅ Demande validée ({conge.get_type()} - pas de déduction)")

            return True

        except Exception as e:
            print(f"❌ Erreur lors de la validation: {e}")
            return False

    def refuser_demande(self, demande_id):
        """Refuse une demande"""
        try:
            row = DemandeDAO.trouver_par_id(demande_id)

            if not row:
                print("❌ Demande introuvable")
                return False

            if row['statut'] != 'En attente':
                print(f"❌ Cette demande a déjà été {row['statut']}")
                return False

            DemandeDAO.mettre_a_jour_statut(demande_id, 'Refusée')
            print("✅ Demande refusée")
            return True

        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

    def lister_demandes_en_attente(self):
        """Liste les demandes en attente avec objets polymorphiques"""
        try:
            rows = DemandeDAO.lister_par_statut('En attente')
            return self._convertir_rows_en_conges(rows)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    def lister_demandes_par_employe(self, employe_id):
        """Liste les demandes d'un employé"""
        try:
            rows = DemandeDAO.lister_par_employe(employe_id)
            return self._convertir_rows_en_conges(rows)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    def lister_demandes_validees(self):
        """Liste les demandes validées"""
        try:
            rows = DemandeDAO.lister_par_statut('Validée')
            return self._convertir_rows_en_conges(rows)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    def lister_demandes_refusees(self):
        """Liste les demandes refusées"""
        try:
            rows = DemandeDAO.lister_par_statut('Refusée')
            return self._convertir_rows_en_conges(rows)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    def _convertir_rows_en_conges(self, rows):
        """
        Méthode privée pour convertir les résultats SQL en objets Conge
        Exemple d'encapsulation: méthode interne non exposée
        """
        conges = []
        for row in rows:
            try:
                conge = CongeFactory.creer_conge(
                    row['type_conge'],
                    row['id'],
                    row['employe_id'],
                    row['date_debut'],
                    row['date_fin'],
                    row['statut'],
                    row['commentaire']
                )
                # Attacher les infos de l'employé pour l'affichage
                conge.nom = row['nom']
                conge.prenom = row['prenom']
                conge.matricule = row['matricule']
                conge.solde_conges = row['solde_conges']
                conge.service = row['service']
                conges.append(conge)
            except ValueError as e:
                print(f"⚠️  Erreur: {e}")
                continue
        return conges

    def get_employe_by_matricule(self, matricule):
        """Récupère un employé par matricule"""
        try:
            return EmployeDAO.trouver_par_matricule(matricule)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None

    def get_employe_by_id(self, employe_id):
        """Récupère un employé par ID"""
        try:
            return EmployeDAO.trouver_par_id(employe_id)
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None