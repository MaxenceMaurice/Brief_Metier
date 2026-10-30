
from datetime import date

from models.user import Apprenant, Admin, NiveauAcces
from permissions import check_permission, PermissionRefusee


def test_apprenant_consulter():
    apprenant = Apprenant(
        nom="Test",
        prenom="Alice",
        email="alice@test.fr",
        date_naissance=date(2000, 1, 1)
    )

    assert check_permission(apprenant, "consulter") is True


def test_apprenant_creer_refuse():
    apprenant = Apprenant(
        nom="Test",
        prenom="Alice",
        email="alice@test.fr",
        date_naissance=date(2000, 1, 1)
    )

    try:
        check_permission(apprenant, "creer")
        assert False, "La permission aurait dû être refusée"
    except PermissionRefusee:
        pass


def test_superadmin_supprimer():
    admin = Admin(
        nom="Test",
        prenom="Bob",
        email="bob@test.fr",
        niveau_acces=NiveauAcces.SUPERADMIN,
        date_promotion=date.today()
    )

    assert check_permission(admin, "supprimer") is True


def test_utilisateur_inactif():
    apprenant = Apprenant(
        nom="Test",
        prenom="Alice",
        email="alice@test.fr",
        date_naissance=date(2000, 1, 1),
        is_active=False
    )

    try:
        check_permission(apprenant, "consulter")
        assert False, "La permission aurait dû être refusée"
    except PermissionRefusee:
        pass
