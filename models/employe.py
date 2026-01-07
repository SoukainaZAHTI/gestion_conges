class Employe:
    def __init__(self, id, matricule, nom, prenom, service, solde_conges):
        self.id = id
        self.matricule = matricule
        self.nom = nom
        self.prenom = prenom
        self.service = service
        self.solde_conges = solde_conges

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom} ({self.service})"

    def a_suffisamment_de_conges(self, jours_demandes):
        return self.solde_conges >= jours_demandes