from database import get_connection
from models.employe import Employe
from models.types_conge import CongeFactory, Conge
from utils.validators import valider_periode


class GestionConges:
    SOLDE_INITIAL_ANNUEL = 22

    def add_employe(self, matricule, nom, prenom, service, solde=None):
        """Ajoute un employé avec un solde par défaut"""
        if solde is None:
            solde = self.SOLDE_INITIAL_ANNUEL

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                        INSERT INTO employes (matricule, nom, prenom, service, solde_conges)
                        VALUES (?, ?, ?, ?, ?)""",
                        (matricule, nom, prenom, service, solde))
            conn.commit()
            print(f"✅ Employé ajouté avec un solde de {solde} jours")
            return True
        except:
            print("❌ Erreur: Ce matricule existe déjà")
            return False
        finally:
            conn.close()

    def list_employes(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employes")
        rows = cur.fetchall()
        conn.close()
        return [Employe(**row) for row in rows]

    def ajouter_demande(self, employe_id, date_debut, date_fin, type_conge, commentaire="", **kwargs):
        """
        Ajoute une demande en utilisant le polymorphisme
        **kwargs permet de passer des paramètres spécifiques (ex: motif pour CongeExceptionnel)
        """
        # Validate dates
        valide, message = valider_periode(date_debut, date_fin)
        if not valide:
            print(f"❌ {message}")
            return False

        conn = get_connection()
        cur = conn.cursor()

        # Get employee info
        cur.execute("SELECT * FROM employes WHERE id = ?", (employe_id,))
        emp_row = cur.fetchone()

        if not emp_row:
            print("❌ Employé non trouvé")
            conn.close()
            return False

        employe = Employe(**emp_row)

        # Create the appropriate Conge object using Factory
        try:
            conge = CongeFactory.creer_conge(
                type_conge,
                None,  # id will be assigned by database
                employe_id,
                date_debut,
                date_fin,
                "En attente",
                commentaire,
                **kwargs
            )
        except ValueError as e:
            print(f"❌ {e}")
            conn.close()
            return False

        # Use polymorphism to validate the request
        valide, message = conge.valider_demande(employe.solde_conges)

        if not valide:
            print(f"❌ {message}")
            conn.close()
            return False

        # Store in database with type_conge string
        cur.execute("""
                    INSERT INTO demandes_conge (employe_id, date_debut, date_fin, type_conge, statut, commentaire)
                    VALUES (?, ?, ?, ?, 'En attente', ?)
                    """, (employe_id, date_debut, date_fin, conge.get_type(), commentaire))

        conn.commit()
        conn.close()

        jours = conge.calculer_jours()
        print(f"✅ Demande de {jours} jours ajoutée ({conge.get_type()})")
        return True

    def valider_demande(self, demande_id):
        """Valide une demande en utilisant le polymorphisme"""
        conn = get_connection()
        cur = conn.cursor()

        # Get full request details with JOIN
        cur.execute("""
                    SELECT d.*, e.solde_conges, e.nom, e.prenom, e.matricule
                    FROM demandes_conge d
                             JOIN employes e ON d.employe_id = e.id
                    WHERE d.id = ?
                    """, (demande_id,))

        row = cur.fetchone()

        if not row:
            print("❌ Demande introuvable")
            conn.close()
            return False

        if row['statut'] != 'En attente':
            print(f"❌ Cette demande a déjà été {row['statut']}")
            conn.close()
            return False

        # Create Conge object using Factory (polymorphism)
        try:
            conge = CongeFactory.creer_conge(
                row['type_conge'],
                row['id'],
                row['employe_id'],
                row['date_debut'],
                row['date_fin'],
                row['statut'],
                row['commentaire']
            )
        except ValueError as e:
            print(f"❌ {e}")
            conn.close()
            return False

        # Validate using polymorphic method
        valide, message = conge.valider_demande(row['solde_conges'])

        if not valide:
            print(f"❌ VALIDATION IMPOSSIBLE!")
            print(f"   Employé: {row['nom']} {row['prenom']}")
            print(f"   {message}")
            conn.close()
            return False

        # Update status
        cur.execute("UPDATE demandes_conge SET statut = 'Validée' WHERE id = ?", (demande_id,))

        # Deduct from balance if needed (polymorphism)
        if conge.deduit_du_solde():
            jours_a_deduire = conge.calculer_jours_deductibles()
            cur.execute(
                "UPDATE employes SET solde_conges = solde_conges - ? WHERE id = ?",
                (jours_a_deduire, row['employe_id'])
            )
            print(f"✅ Demande validée - {jours_a_deduire} jours déduits")
        else:
            print(f"✅ Demande validée ({conge.get_type()} - pas de déduction)")

        conn.commit()
        conn.close()
        return True

    def refuser_demande(self, demande_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT statut FROM demandes_conge WHERE id = ?", (demande_id,))
        result = cur.fetchone()

        if not result:
            print("❌ Demande introuvable")
            conn.close()
            return False

        if result['statut'] != 'En attente':
            print(f"❌ Cette demande a déjà été {result['statut']}")
            conn.close()
            return False

        cur.execute("UPDATE demandes_conge SET statut = 'Refusée' WHERE id = ?", (demande_id,))
        conn.commit()
        conn.close()
        print("✅ Demande refusée")
        return True

    def lister_demandes_en_attente(self):
        """Liste toutes les demandes en attente avec objets polymorphiques"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT d.*, e.nom, e.prenom, e.matricule, e.solde_conges, e.service
                    FROM demandes_conge d
                             JOIN employes e ON d.employe_id = e.id
                    WHERE d.statut = 'En attente'
                    ORDER BY d.date_debut
                    """)
        rows = cur.fetchall()
        conn.close()

        # Convert to Conge objects with employee info attached
        conges = []
        for row in rows:
            conge = CongeFactory.creer_conge(
                row['type_conge'],
                row['id'],
                row['employe_id'],
                row['date_debut'],
                row['date_fin'],
                row['statut'],
                row['commentaire']
            )
            # Attach employee info for display
            conge.nom = row['nom']
            conge.prenom = row['prenom']
            conge.matricule = row['matricule']
            conge.solde_conges = row['solde_conges']
            conge.service = row['service']
            conges.append(conge)

        return conges

    def get_employe_by_matricule(self, matricule):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employes WHERE matricule = ?", (matricule,))
        row = cur.fetchone()
        conn.close()
        return Employe(**row) if row else None

    def get_employe_by_id(self, employe_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employes WHERE id = ?", (employe_id,))
        row = cur.fetchone()
        conn.close()
        return Employe(**row) if row else None

    def lister_demandes_par_employe(self, employe_id):
        """Liste toutes les demandes d'un employé spécifique"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT d.*, e.nom, e.prenom, e.matricule, e.solde_conges, e.service
                    FROM demandes_conge d
                             JOIN employes e ON d.employe_id = e.id
                    WHERE d.employe_id = ?
                    ORDER BY d.date_debut DESC
                    """, (employe_id,))
        rows = cur.fetchall()
        conn.close()

        # Convert to Conge objects with employee info attached
        conges = []
        for row in rows:
            try:
                conge = CongeFactory.creer_conge(
                    row['type_conge'],
                    row['id'],
                    row['employe_id'],
                    row['date_debut'],
                    row['date_fin'],
                    row['statut'],
                    row['commentaire']
                )
                # Attach employee info for display
                conge.nom = row['nom']
                conge.prenom = row['prenom']
                conge.matricule = row['matricule']
                conge.solde_conges = row['solde_conges']
                conge.service = row['service']
                conges.append(conge)
            except ValueError as e:
                print(f"⚠️  Erreur lors du chargement de la demande {row['id']}: {e}")
                continue

        return conges