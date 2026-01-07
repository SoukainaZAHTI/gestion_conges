from datetime import datetime


def valider_format_date(date_str):
    """Valide que la date est au format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Format de date invalide (utilisez YYYY-MM-DD)"


def valider_periode(date_debut, date_fin):
    """Valide que date_fin est après date_debut"""
    try:
        debut = datetime.strptime(date_debut, '%Y-%m-%d')
        fin = datetime.strptime(date_fin, '%Y-%m-%d')

        if fin < debut:
            return False, "La date de fin doit être après la date de début"

        return True, ""
    except ValueError as e:
        return False, str(e)


def valider_matricule(matricule):
    """Valide le format du matricule"""
    if not matricule or len(matricule) < 3:
        return False, "Matricule invalide (minimum 3 caractères)"
    return True, ""


def valider_solde(solde):
    """Valide que le solde est un nombre positif"""
    try:
        solde_int = int(solde)
        if solde_int < 0:
            return False, "Le solde ne peut pas être négatif"
        return True, ""
    except ValueError:
        return False, "Le solde doit être un nombre entier"