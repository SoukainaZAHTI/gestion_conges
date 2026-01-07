class DemandeConge:
    def __init__(self, id, employe_id, date_debut, date_fin, type_conge, statut, commentaire):
        self.id = id
        self.employe_id = employe_id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.type_conge = type_conge
        self.statut = statut
        self.commentaire = commentaire

    def __str__(self):
        return f"Demande {self.id} | Emp: {self.employe_id} | {self.date_debut} → {self.date_fin} | {self.statut}"
