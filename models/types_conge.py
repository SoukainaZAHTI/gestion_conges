from datetime import datetime
from abc import ABC, abstractmethod


class Conge(ABC):
    """
    Classe de base abstraite pour tous les types de congés
    Implémente le polymorphisme pour les règles métier spécifiques
    """

    def __init__(self, id, employe_id, date_debut, date_fin, statut, commentaire=""):
        self.id = id
        self.employe_id = employe_id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.statut = statut
        self.commentaire = commentaire

    @abstractmethod
    def get_type(self):
        """Retourne le type de congé (à implémenter dans chaque sous-classe)"""
        pass

    @abstractmethod
    def necessite_validation_solde(self):
        """Indique si ce type de congé nécessite une vérification du solde"""
        pass

    @abstractmethod
    def deduit_du_solde(self):
        """Indique si ce type de congé déduit du solde de l'employé"""
        pass

    def calculer_jours(self):
        """Calcule le nombre de jours entre date_debut et date_fin"""
        debut = datetime.strptime(self.date_debut, '%Y-%m-%d')
        fin = datetime.strptime(self.date_fin, '%Y-%m-%d')
        return (fin - debut).days + 1

    def calculer_jours_deductibles(self):
        """
        Calcule les jours à déduire (peut être surchargé)
        Par défaut, retourne le nombre total de jours
        """
        return self.calculer_jours()

    def valider_demande(self, solde_actuel):
        """
        Valide si la demande peut être acceptée
        Retourne (bool, message)
        """
        if not self.necessite_validation_solde():
            return True, "Validation OK (pas de vérification de solde requise)"

        jours_necessaires = self.calculer_jours_deductibles()
        if jours_necessaires > solde_actuel:
            return False, f"Solde insuffisant: {jours_necessaires} jours demandés, {solde_actuel} disponibles"

        return True, "Validation OK"

    def __str__(self):
        return f"Demande {self.id} | {self.get_type()} | {self.date_debut} → {self.date_fin} | {self.statut}"


class CongeAnnuel(Conge):
    """
    Congé annuel payé - déduit du solde de l'employé
    """

    def get_type(self):
        return "Annuel"

    def necessite_validation_solde(self):
        return True

    def deduit_du_solde(self):
        return True

    def get_emoji(self):
        return "🏖️"


class CongeMaladie(Conge):
    """
    Congé maladie - ne déduit PAS du solde, mais nécessite justificatif
    """

    def get_type(self):
        return "Maladie"

    def necessite_validation_solde(self):
        return False  # Pas de vérification de solde

    def deduit_du_solde(self):
        return False  # Ne déduit pas du solde

    def get_emoji(self):
        return "🏥"

    def necessite_justificatif(self):
        """Congé maladie > 3 jours nécessite un certificat médical"""
        return self.calculer_jours() > 3


class CongeExceptionnel(Conge):
    """
    Congé exceptionnel (mariage, décès, etc.) - ne déduit PAS du solde
    Durée limitée selon l'événement
    """

    DUREES_AUTORISEES = {
        "mariage": 4,
        "naissance": 3,
        "deces_proche": 3,
        "demenagement": 1
    }

    def __init__(self, id, employe_id, date_debut, date_fin, statut, commentaire="", motif=""):
        super().__init__(id, employe_id, date_debut, date_fin, statut, commentaire)
        self.motif = motif.lower()

    def get_type(self):
        return "Exceptionnel"

    def necessite_validation_solde(self):
        return False

    def deduit_du_solde(self):
        return False

    def get_emoji(self):
        return "🎉"

    def get_duree_maximale(self):
        """Retourne la durée maximale autorisée pour ce motif"""
        return self.DUREES_AUTORISEES.get(self.motif, 0)

    def valider_demande(self, solde_actuel):
        """Surcharge pour vérifier la durée selon le motif"""
        if self.motif not in self.DUREES_AUTORISEES:
            return False, f"Motif '{self.motif}' non reconnu. Motifs valides: {', '.join(self.DUREES_AUTORISEES.keys())}"

        jours_demandes = self.calculer_jours()
        jours_max = self.get_duree_maximale()

        if jours_demandes > jours_max:
            return False, f"Durée maximale pour '{self.motif}': {jours_max} jours (demandé: {jours_demandes})"

        return True, "Validation OK"


class CongeSansSolde(Conge):
    """
    Congé sans solde - ne déduit PAS du solde mais n'est pas payé
    """

    def get_type(self):
        return "Sans solde"

    def necessite_validation_solde(self):
        return False

    def deduit_du_solde(self):
        return False

    def get_emoji(self):
        return "💼"


class CongeParental(Conge):
    """
    Congé parental - règles spéciales, peut être fractionné
    """

    DUREE_MAXIMALE_ANNEE = 120  # 4 mois par an

    def get_type(self):
        return "Parental"

    def necessite_validation_solde(self):
        return False

    def deduit_du_solde(self):
        return False

    def get_emoji(self):
        return "👶"

    def valider_demande(self, solde_actuel):
        """Vérification spécifique au congé parental"""
        jours = self.calculer_jours()
        if jours > self.DUREE_MAXIMALE_ANNEE:
            return False, f"Durée maximale de congé parental: {self.DUREE_MAXIMALE_ANNEE} jours par an"
        return True, "Validation OK"


# Factory pour créer les bons objets selon le type
class CongeFactory:
    """
    Factory Pattern: crée la bonne instance de congé selon le type
    """

    @staticmethod
    def creer_conge(type_conge, id, employe_id, date_debut, date_fin, statut, commentaire="", **kwargs):
        """
        Crée une instance du bon type de congé

        Args:
            type_conge: "Annuel", "Maladie", "Exceptionnel", etc.
            **kwargs: paramètres supplémentaires (ex: motif pour CongeExceptionnel)
        """
        type_map = {
            "annuel": CongeAnnuel,
            "maladie": CongeMaladie,
            "exceptionnel": CongeExceptionnel,
            "sans solde": CongeSansSolde,
            "parental": CongeParental
        }

        classe_conge = type_map.get(type_conge.lower())

        if not classe_conge:
            raise ValueError(f"Type de congé inconnu: {type_conge}")

        # CongeExceptionnel nécessite un motif
        if classe_conge == CongeExceptionnel:
            motif = kwargs.get('motif', '')
            return classe_conge(id, employe_id, date_debut, date_fin, statut, commentaire, motif)

        return classe_conge(id, employe_id, date_debut, date_fin, statut, commentaire)