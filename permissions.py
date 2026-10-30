
from models.user import Apprenant, Formateur, StaffPedagogique, Admin, NiveauAcces


class PermissionRefusee(Exception):
    """Erreur lorsqu'un utilisateur n'a pas les droits nécessaires."""
    pass


def check_permission(utilisateur, action):
    """Vérifie si un utilisateur peut effectuer une action."""

    if not utilisateur.is_active:
        raise PermissionRefusee("Cet utilisateur est désactivé.")

    if isinstance(utilisateur, Admin):
        if utilisateur.niveau_acces == NiveauAcces.SUPERADMIN:
            return True

        if action in ["consulter", "creer", "modifier"]:
            return True

    elif isinstance(utilisateur, StaffPedagogique):
        if action in ["consulter", "creer", "modifier"]:
            return True

    elif isinstance(utilisateur, Formateur):
        if action in ["consulter", "modifier"]:
            return True

    elif isinstance(utilisateur, Apprenant):
        if action == "consulter":
            return True

    raise PermissionRefusee(
        f"Permission refusée pour l'action : {action}"
    )
