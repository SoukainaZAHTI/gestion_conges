#Système de Gestion des Congés — Guide d’exécution
Ce document explique comment initialiser la base de données, lancer l’application et exécuter le scénario de test minimal.

##Initialisation de la base de données#

Dans le dossier du projet, exécuter :
python -c "from database import init_db; init_db()"
Cela crée le fichier conges.db avec les tables nécessaires.


Pour réinitialiser complètement la base (⚠️ supprime toutes les données) :
python -c "from database import reset_db; reset_db()"

##Lancer le script principal#
python main.py

Le menu principal s’affiche :
1. Se connecter
2. Créer un compte employé
3. Quitter

Vous pouvez ensuite :
1.créer un compte,
2.vous connecter,
3.ajouter des demandes de congé,
ou, avec un compte RH, valider/refuser les demandes.


##Reproduire le scénario de test minimal#

Exécuter le script de test automatisé :
python test.py

Ce script :

1.Réinitialise la base,
2.Crée des employés et utilisateurs de test,
3.Crée plusieurs demandes (valides et invalides),
4.Valide/refuse automatiquement les demandes,
5.Affiche les soldes finaux et statistiques.

Aucune action manuelle n’est nécessaire.




