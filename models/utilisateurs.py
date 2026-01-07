class Utilisateur:
    def __init__(self, id, login, mot_de_passe, role):
        self.id = id
        self.login = login
        self.mot_de_passe = mot_de_passe
        self.role = role

    def est_rh(self):
        return self.role == "RH"
