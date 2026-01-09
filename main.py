from database import init_db
from services.gestion_conges import GestionConges
from services.authentification import ServiceAuthentification
from utils.display import afficher_demande_detaillee, afficher_liste_employes, afficher_menu_types_conge
from models.types_conge import CongeExceptionnel


def menu_principal():
    print("\n=== Système de Gestion des Congés ===")
    print("1. Se connecter")
    print("2. Créer un compte employé")
    print("3. Quitter")
    return input("Choisir une option >> ")


def menu_employe():
    print("\n=== Menu Employé ===")
    print("1. Ajouter une demande de congé")
    print("2. Voir mes demandes")
    print("3. Se déconnecter")
    return input("Choisir une option >> ")


def menu_rh():
    print("\n=== Menu RH ===")
    print("1. Ajouter un employé")
    print("2. Lister les employés")
    print("3. Voir demandes EN ATTENTE")
    print("4. Valider une demande")
    print("5. Refuser une demande")
    print("6. Se déconnecter")
    return input("Choisir une option >> ")


def main():
    init_db()
    gc = GestionConges()
    auth = ServiceAuthentification()
    utilisateur_connecte = None

    while True:
        if utilisateur_connecte is None:
            choix = menu_principal()

            if choix == "1":
                login = input("Login: ")
                mdp = input("Mot de passe: ")
                utilisateur_connecte = auth.authentifier(login, mdp)

                if utilisateur_connecte:
                    print(f"\n✅ Bienvenue {utilisateur_connecte.login} ({utilisateur_connecte.role})")
                else:
                    print("❌ Identifiants incorrects")


            elif choix == "2":

                login = input("Nouveau login: ")

                mdp = input("Mot de passe: ")

                matricule = input("Votre matricule: ")

                nom = input("Nom: ")

                prenom = input("Prénom: ")

                service = input("Service: ")

                emp = gc.get_employe_by_matricule(matricule)

                if emp:

                    print("ℹ️ Employé existant détecté")

                    # Create only the user account

                    if auth.creer_utilisateur(login, mdp, "Employe"):
                        print("✅ Compte utilisateur créé et lié à l’employé existant")


                else:

                    print("ℹ️ Nouvel employé — création employé + compte")

                    if auth.creer_utilisateur(login, mdp, "Employe"):
                        gc.add_employe(matricule, nom, prenom, service)

                        print("✅ Employé et compte créés avec succès")


            elif choix == "3":
                print("Au revoir!")
                break

        else:
            if utilisateur_connecte.est_rh():
                choix = menu_rh()

                if choix == "1":
                    # Add employee
                    m = input("Matricule: ")
                    n = input("Nom: ")
                    p = input("Prénom: ")
                    s = input("Service: ")
                    custom = input("Utiliser solde personnalisé? (o/N): ").lower()

                    if custom == "o":
                        sol = int(input("Solde congés: "))
                        gc.add_employe(m, n, p, s, sol)
                    else:
                        gc.add_employe(m, n, p, s)

                elif choix == "2":
                    # List employees
                    employes = gc.list_employes()
                    afficher_liste_employes(employes)

                elif choix == "3":
                    # Show pending requests with polymorphism
                    print("\n" + "=" * 60)
                    print("DEMANDES EN ATTENTE")
                    print("=" * 60)
                    demandes = gc.lister_demandes_en_attente()

                    if demandes:
                        for conge in demandes:
                            afficher_demande_detaillee(conge, conge.solde_conges)
                    else:
                        print("✅ Aucune demande en attente")

                elif choix == "4":
                    # Validate request
                    demandes = gc.lister_demandes_en_attente()

                    if not demandes:
                        print("✅ Aucune demande en attente")
                    else:
                        for conge in demandes:
                            jours = conge.calculer_jours()
                            deduit = "💰" if conge.deduit_du_solde() else "ℹ️ "
                            print(
                                f"ID {conge.id}: {conge.nom} | {conge.get_emoji()} {conge.get_type()} | {jours}j | {deduit}")

                        did = int(input("\nID de la demande à valider : "))
                        gc.valider_demande(did)

                elif choix == "5":
                    # Refuse request
                    demandes = gc.lister_demandes_en_attente()

                    if not demandes:
                        print("✅ Aucune demande en attente")
                    else:
                        for conge in demandes:
                            print(
                                f"ID {conge.id}: {conge.nom} | {conge.get_type()} | {conge.date_debut} → {conge.date_fin}")

                        did = int(input("\nID de la demande à refuser : "))
                        gc.refuser_demande(did)

                elif choix == "6":
                    utilisateur_connecte = None
                    print("Déconnexion réussie")

            else:
                # Employee menu
                choix = menu_employe()

                if choix == "1":
                    # Add leave request
                    mat = input("Votre matricule: ")
                    emp = gc.get_employe_by_matricule(mat)

                    if emp:
                        print(f"✅ Employé: {emp.nom} {emp.prenom}")
                        print(f"📊 Solde actuel: {emp.solde_conges} jours")

                        # Show available leave types
                        afficher_menu_types_conge()

                        choix_type = input("\nChoisir le type (1-5): ")

                        type_map = {
                            "1": "Annuel",
                            "2": "Maladie",
                            "3": "Exceptionnel",
                            "4": "Sans solde",
                            "5": "Parental"
                        }

                        type_conge = type_map.get(choix_type)

                        if not type_conge:
                            print("❌ Type invalide")
                            continue

                        dd = input("Date début (YYYY-MM-DD): ")
                        df = input("Date fin (YYYY-MM-DD): ")
                        com = input("Commentaire: ")

                        # Special handling for CongeExceptionnel
                        kwargs = {}
                        if type_conge == "Exceptionnel":
                            print("\nMotifs disponibles: mariage, naissance, deces_proche, demenagement")
                            motif = input("Motif: ")
                            kwargs['motif'] = motif

                        gc.ajouter_demande(emp.id, dd, df, type_conge, com, **kwargs)
                    else:
                        print("❌ Matricule non trouvé")

                elif choix == "2":
                    # View my requests
                    mat = input("Votre matricule: ")
                    emp = gc.get_employe_by_matricule(mat)

                    if emp:
                        print(f"\n{'=' * 60}")
                        print(f"MES DEMANDES - {emp.nom} {emp.prenom}")
                        print(f"{'=' * 60}")

                        # Get all requests for this employee
                        demandes = gc.lister_demandes_par_employe(emp.id)

                        if demandes:
                            for conge in demandes:
                                afficher_demande_detaillee(conge, emp.solde_conges)
                        else:
                            print("Vous n'avez aucune demande enregistrée")
                    else:
                        print("❌ Matricule non trouvé")

                elif choix == "3":
                    utilisateur_connecte = None
                    print("Déconnexion réussie")


if __name__ == "__main__":
    main()