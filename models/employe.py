class Employe:
    def __init__(self, id, matricule, nom, prenom, service, solde_conges):
        self.__id = id  # Private
        self.__matricule = matricule  # Private
        self.__nom = nom  # Private
        self.__prenom = prenom  # Private
        self.__service = service  # Private



        self.__solde_conges = solde_conges  # Private

    # Getters (accessors)
    @property
    def id(self):
        return self.__id

    @property
    def matricule(self):
        return self.__matricule

    @property
    def nom(self):
        return self.__nom

    @property
    def prenom(self):
        return self.__prenom

    @property
    def service(self):
        return self.__service

    @property
    def solde_conges(self):
        return self.__solde_conges

    # Setter with validation (protects data integrity)
    @solde_conges.setter
    def solde_conges(self, valeur):
        """Empêche un solde négatif - exemple d'encapsulation"""
        if valeur < 0:
            raise ValueError("Le solde de congés ne peut pas être négatif")
        self.__solde_conges = valeur

    def deduire_conges(self, jours):
        """
        Déduit des jours de congé avec validation
        Exemple de méthode qui protège l'intégrité des données
        """
        if jours > self.__solde_conges:
            raise ValueError(f"Solde insuffisant: {jours} jours demandés, {self.__solde_conges} disponibles")
        self.__solde_conges -= jours
        return self.__solde_conges

    def ajouter_conges(self, jours):
        """Ajoute des jours au solde (ex: nouvelle année)"""
        if jours < 0:
            raise ValueError("Impossible d'ajouter un nombre négatif de jours")
        self.__solde_conges += jours
        return self.__solde_conges

    def __str__(self):
        return f"{self.__matricule} - {self.__nom} {self.__prenom} ({self.__service})"