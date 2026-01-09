"""
Script de démonstration et test du système de gestion des congés
Ce script exécute un scénario complet pour valider toutes les fonctionnalités
"""
from database import init_db, reset_db
from services.gestion_conges import GestionConges
from services.authentification import ServiceAuthentification
from services.dao import EmployeDAO, DemandeDAO, UtilisateurDAO
from datetime import datetime


def afficher_titre(titre):
    """Affiche un titre formaté"""
    print(f"\n{'=' * 70}")
    print(f"  {titre}")
    print('=' * 70)


def afficher_employes(gc):
    """Affiche tous les employés avec leur solde"""
    employes = gc.list_employes()
    print(f"\n{'MATRICULE':<12} | {'NOM':<15} | {'PRÉNOM':<15} | {'SERVICE':<15} | {'SOLDE':<8}")
    print('-' * 80)
    for e in employes:
        print(f"{e.matricule:<12} | {e.nom:<15} | {e.prenom:<15} | {e.service:<15} | {e.solde_conges:>3} jours")


def afficher_demandes(demandes, titre="DEMANDES"):
    """Affiche une liste de demandes"""
    print(f"\n{titre}")
    print('-' * 80)
    if not demandes:
        print("  Aucune demande")
        return

    for d in demandes:
        jours = d.calculer_jours()
        deduit = "💰 Déduit" if d.deduit_du_solde() else "ℹ️  Non déduit"
        emoji = d.get_emoji() if hasattr(d, 'get_emoji') else '📄'
        print(f"  ID {d.id}: {d.nom} {d.prenom} | {emoji} {d.get_type()} | "
              f"{d.date_debut} → {d.date_fin} ({jours}j) | {d.statut} | {deduit}")


def scenario_complet():
    """
    Scénario de test complet qui démontre toutes les fonctionnalités
    """

    # ============================================================================
    # ÉTAPE 1: INITIALISATION DE LA BASE
    # ============================================================================
    afficher_titre("ÉTAPE 1: INITIALISATION DE LA BASE DE DONNÉES")
    print("Réinitialisation complète de la base...")
    reset_db()
    init_db()

    gc = GestionConges()
    auth = ServiceAuthentification()

    # ============================================================================
    # ÉTAPE 2: CRÉATION DES UTILISATEURS
    # ============================================================================
    afficher_titre("ÉTAPE 2: CRÉATION DES COMPTES UTILISATEURS")

    print("\n🔐 Création du compte RH...")
    auth.creer_utilisateur("admin", "admin", "RH")

    print("\n🔐 Création des comptes employés...")
    auth.creer_utilisateur("alice.martin", "pass1", "Employe")
    auth.creer_utilisateur("bob.dupont", "pass2", "Employe")
    auth.creer_utilisateur("claire.bernard", "pass3", "Employe")
    auth.creer_utilisateur("david.moreau", "pass4", "Employe")

    # ============================================================================
    # ÉTAPE 3: CRÉATION DES EMPLOYÉS
    # ============================================================================
    afficher_titre("ÉTAPE 3: CRÉATION DES EMPLOYÉS")

    print("\n👤 Ajout d'Alice Martin (solde standard: 22 jours)...")
    gc.add_employe("EMP001", "Martin", "Alice", "Informatique", 22)

    print("\n👤 Ajout de Bob Dupont (solde faible: 5 jours)...")
    gc.add_employe("EMP002", "Dupont", "Bob", "Comptabilité", 5)

    print("\n👤 Ajout de Claire Bernard (solde élevé: 30 jours)...")
    gc.add_employe("EMP003", "Bernard", "Claire", "Marketing", 30)

    print("\n👤 Ajout de David Moreau (nouveau: 15 jours)...")
    gc.add_employe("EMP004", "Moreau", "David", "RH", 15)

    print("\n📊 État initial des employés:")
    afficher_employes(gc)

    # ============================================================================
    # ÉTAPE 4: CRÉATION DES DEMANDES DE CONGÉ
    # ============================================================================
    afficher_titre("ÉTAPE 4: CRÉATION DES DEMANDES DE CONGÉ")

    # Récupération des employés
    alice = gc.get_employe_by_matricule("EMP001")
    bob = gc.get_employe_by_matricule("EMP002")
    claire = gc.get_employe_by_matricule("EMP003")
    david = gc.get_employe_by_matricule("EMP004")

    print("\n📝 DEMANDES VALIDES:")

    # Alice - Congé annuel valide
    print("\n1. Alice demande 10 jours de congé annuel (solde: 22j)")
    gc.ajouter_demande(
        alice.id,
        "2026-02-10",
        "2026-02-19",
        "Annuel",
        "Vacances d'hiver à la montagne"
    )

    # Claire - Congé maladie
    print("\n2. Claire demande 5 jours de congé maladie")
    gc.ajouter_demande(
        claire.id,
        "2026-01-15",
        "2026-01-19",
        "Maladie",
        "Grippe"
    )

    # David - Congé exceptionnel
    print("\n3. David demande 4 jours de congé exceptionnel (mariage)")
    gc.ajouter_demande(
        david.id,
        "2026-03-10",
        "2026-03-13",
        "Exceptionnel",
        "Mon mariage",
        motif="mariage"
    )

    # Alice - Congé parental
    print("\n4. Alice demande 30 jours de congé parental")
    gc.ajouter_demande(
        alice.id,
        "2026-04-01",
        "2026-04-30",
        "Parental",
        "Naissance de mon enfant"
    )

    print("\n\n📝 DEMANDES INVALIDES (vont échouer):")

    # Bob - Solde insuffisant
    print("\n5. Bob demande 10 jours mais n'a que 5 jours de solde:")
    gc.ajouter_demande(
        bob.id,
        "2026-02-01",
        "2026-02-10",
        "Annuel",
        "Tentative avec solde insuffisant"
    )

    # Claire - Congé exceptionnel trop long
    print("\n6. Claire demande 10 jours de congé exceptionnel (mariage, max 4j):")
    gc.ajouter_demande(
        claire.id,
        "2026-03-01",
        "2026-03-10",
        "Exceptionnel",
        "Mariage - durée excessive",
        motif="mariage"
    )

    # Bob - Congé valide avec son petit solde
    print("\n7. Bob demande 3 jours (compatible avec son solde de 5j):")
    gc.ajouter_demande(
        bob.id,
        "2026-02-15",
        "2026-02-17",
        "Annuel",
        "Court séjour"
    )

    # ============================================================================
    # ÉTAPE 5: CONSULTATION DES DEMANDES EN ATTENTE
    # ============================================================================
    afficher_titre("ÉTAPE 5: DEMANDES EN ATTENTE (VUE RH)")

    demandes_attente = gc.lister_demandes_en_attente()
    afficher_demandes(demandes_attente, "📋 DEMANDES À TRAITER")

    print(f"\n✅ {len(demandes_attente)} demande(s) en attente de validation")

    # ============================================================================
    # ÉTAPE 6: VALIDATION/REFUS PAR LE RH
    # ============================================================================
    afficher_titre("ÉTAPE 6: TRAITEMENT PAR LE RESPONSABLE RH")

    # Authentification du RH
    print("\n🔐 Connexion du responsable RH...")
    rh = auth.authentifier("admin", "admin")

    if rh and auth.verifier_acces_rh(rh):
        print(f"✅ {rh.login} connecté avec droits RH")

        # Traiter chaque demande
        for demande in demandes_attente:
            print(f"\n📋 Traitement de la demande ID {demande.id}:")
            print(f"   Employé: {demande.nom} {demande.prenom}")
            print(f"   Type: {demande.get_type()}")
            print(f"   Période: {demande.date_debut} → {demande.date_fin}")
            print(f"   Jours: {demande.calculer_jours()}")

            # Valider les demandes ID 1, 2, 3, 4, 5 (5 est la demande de Bob avec 3 jours)
            # Les IDs peuvent varier selon l'ordre de création
            # On va valider les demandes valides et refuser les autres

            # Simuler la décision du RH
            emp = EmployeDAO.trouver_par_id(demande.employe_id)
            peut_valider, message = demande.valider_demande(emp.solde_conges)

            if peut_valider:
                print(f"   ✅ Validation de la demande...")
                gc.valider_demande(demande.id)
            else:
                print(f"   ❌ Refus: {message}")
                gc.refuser_demande(demande.id)

    # ============================================================================
    # ÉTAPE 7: RÉSULTATS FINAUX
    # ============================================================================
    afficher_titre("ÉTAPE 7: RÉSULTATS FINAUX")

    print("\n📊 SOLDES FINAUX DES EMPLOYÉS:")
    afficher_employes(gc)

    print("\n\n📈 HISTORIQUE DÉTAILLÉ PAR EMPLOYÉ:")

    for emp in [alice, bob, claire, david]:
        print(f"\n{'=' * 70}")
        print(f"👤 {emp.nom} {emp.prenom} (Matricule: {emp.matricule})")
        print(f"   Service: {emp.service}")

        # Solde actuel (après validation)
        emp_actuel = EmployeDAO.trouver_par_id(emp.id)
        print(f"   💰 Solde actuel: {emp_actuel.solde_conges} jours")

        # Historique des demandes
        demandes = gc.lister_demandes_par_employe(emp.id)

        if demandes:
            print(f"\n   📋 Historique des demandes ({len(demandes)}):")
            for d in demandes:
                jours = d.calculer_jours()
                deduit = " (déduit)" if d.deduit_du_solde() else ""
                emoji_status = {'En attente': '⏳', 'Validée': '✅', 'Refusée': '❌'}
                status = emoji_status.get(d.statut, '❓')
                emoji_type = d.get_emoji() if hasattr(d, 'get_emoji') else '📄'

                print(f"      {status} ID {d.id}: {emoji_type} {d.get_type()} | "
                      f"{d.date_debut} → {d.date_fin} ({jours}j{deduit})")
                if d.commentaire:
                    print(f"         💬 {d.commentaire}")
        else:
            print("   Aucune demande enregistrée")

    # ============================================================================
    # STATISTIQUES GLOBALES
    # ============================================================================
    afficher_titre("STATISTIQUES GLOBALES")

    toutes_demandes = DemandeDAO.lister_toutes()
    validees = [d for d in toutes_demandes if d['statut'] == 'Validée']
    refusees = [d for d in toutes_demandes if d['statut'] == 'Refusée']
    attente = [d for d in toutes_demandes if d['statut'] == 'En attente']

    print(f"\n📊 Nombre total de demandes: {len(toutes_demandes)}")
    print(f"   ✅ Validées: {len(validees)}")
    print(f"   ❌ Refusées: {len(refusees)}")
    print(f"   ⏳ En attente: {len(attente)}")

    # Calcul des jours totaux
    jours_valides = sum(
        (datetime.strptime(d['date_fin'], '%Y-%m-%d') -
         datetime.strptime(d['date_debut'], '%Y-%m-%d')).days + 1
        for d in validees
    )
    print(f"\n📅 Total de jours de congé validés: {jours_valides} jours")

    print("\n" + "=" * 70)
    print("✅ Scénario de test terminé avec succès!")
    print("=" * 70)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║        SYSTÈME DE GESTION DES CONGÉS - SCÉNARIO DE TEST         ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    try:
        scenario_complet()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()