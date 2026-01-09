class Utilisateur:
    def __init__(self, id, login, mot_de_passe, role):
        self.__id = id
        self.__login = login
        self.__mot_de_passe = mot_de_passe  # Should be hashed in production!
        self.__role = role

    @property
    def id(self):
        return self.__id

    @property
    def login(self):
        return self.__login

    @property
    def role(self):
        return self.__role

    def est_rh(self):
        """Vérifie si l'utilisateur a le rôle RH"""
        return self.__role == "RH"

    def est_employe(self):
        """Vérifie si l'utilisateur a le rôle Employé"""
        return self.__role == "Employe"

    def peut_valider_demandes(self):
        """Vérifie si l'utilisateur peut valider/refuser des demandes"""
        return self.est_rh()

    def verifier_mot_de_passe(self, mot_de_passe):
        """Vérifie le mot de passe (exemple d'encapsulation)"""
        return self.__mot_de_passe == mot_de_passe