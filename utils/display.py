def afficher_demande_detaillee(conge, solde_employe=None):
    """
    Affiche une demande de congé avec tous les détails
    Utilise le polymorphisme pour afficher l'emoji et les infos spécifiques
    """
    jours = conge.calculer_jours()

    # Status emoji
    status_emoji = {
        'En attente': '⏳',
        'Validée': '✅',
        'Refusée': '❌'
    }
    emoji_status = status_emoji.get(conge.statut, '❓')

    # Type emoji (polymorphisme)
    emoji_type = conge.get_emoji() if hasattr(conge, 'get_emoji') else '📄'

    print(f"\n{'=' * 60}")
    print(f"ID: {conge.id} | {emoji_status} {conge.statut} | {emoji_type} {conge.get_type()}")

    # Employee info (if available)
    if hasattr(conge, 'nom'):
        print(f"Employé: {conge.nom} {conge.prenom} (Mat: {conge.matricule})")
    if hasattr(conge, 'service'):
        print(f"Service: {conge.service}")

    print(f"Période: {conge.date_debut} → {conge.date_fin} ({jours} jours)")

    # Show balance info if relevant
    if conge.deduit_du_solde() and solde_employe is not None:
        print(f"💰 Solde actuel: {solde_employe} jours")
        print(f"📉 Sera déduit: {conge.calculer_jours_deductibles()} jours")
    elif not conge.deduit_du_solde():
        print(f"ℹ️  Ne déduit pas du solde")

    # Specific info for CongeExceptionnel
    if isinstance(conge, CongeExceptionnel):
        print(f"Motif: {conge.motif} (Max: {conge.get_duree_maximale()} jours)")

    # Specific info for CongeMaladie
    if isinstance(conge, CongeMaladie) and conge.necessite_justificatif():
        print(f"⚠️  Justificatif médical requis (> 3 jours)")

    if conge.commentaire:
        print(f"Commentaire: {conge.commentaire}")

    print(f"{'=' * 60}")


def afficher_liste_employes(employes):
    """Affiche la liste des employés de manière formatée"""
    print("\n" + "=" * 80)
    print(f"{'MATRICULE':<12} | {'NOM':<15} | {'PRÉNOM':<15} | {'SERVICE':<15} | {'SOLDE':<8}")
    print("=" * 80)
    for e in employes:
        print(f"{e.matricule:<12} | {e.nom:<15} | {e.prenom:<15} | {e.service:<15} | {e.solde_conges:>3} jours")
    print("=" * 80)


def afficher_menu_types_conge():
    """Affiche les types de congé disponibles"""
    print("\n📋 Types de congé disponibles:")
    print("  1. 🏖️  Annuel       - Déduit du solde")
    print("  2. 🏥 Maladie      - Ne déduit pas du solde (justificatif si > 3j)")
    print("  3. 🎉 Exceptionnel - Ne déduit pas (mariage, naissance, décès, déménagement)")
    print("  4. 💼 Sans solde   - Ne déduit pas du solde, non payé")
    print("  5. 👶 Parental     - Ne déduit pas (max 120j/an)")


# Import CongeExceptionnel for isinstance check
from models.types_conge import CongeExceptionnel, CongeMaladie