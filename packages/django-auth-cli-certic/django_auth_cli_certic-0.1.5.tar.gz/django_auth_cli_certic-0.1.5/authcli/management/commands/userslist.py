from django.contrib.auth.models import User
from django.core import serializers
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "-a",
            "--active",
            action="store_true",
            help="afficher uniquement les utilisateurs actifs",
        )
        parser.add_argument(
            "-j", "--json", action="store_true", help="afficher les données en JSON"
        )
        parser.add_argument(
            "-t", "--tabulate", action="store_true", help="afficher les données tabulées"
        )
        parser.add_argument(
            "-s", "--separator", default="|", help="séparateur de champs"
        )

    def handle(self, *args, **options):
        only_active = options["active"]
        print_as_json = options["json"]
        print_tabulate = options["tabulate"]
        sep = options["separator"]
        q = User.objects.all()
        if only_active:
            q = User.objects.filter(is_active=True)
        if print_as_json:
            print(serializers.serialize("json", q, indent=2))
        elif print_tabulate:
            sep = "| "
            print("{:<5}{sep}{:<30}{sep}{:<10}{sep}{:<15}{sep}{:<10}{sep}{} ".format('id', 'username', 'is_active',
                                                                                     'is_superuser', 'is_staff',
                                                                                     'last_login', sep=sep))
            for user in q:
                print("{:<5}{sep}{:<30}{sep}{:<10}{sep}{:<15}{sep}{:<10}{sep}{} ".format(user.pk, user.username,
                                                                                         user.is_active,
                                                                                         user.is_superuser,
                                                                                         user.is_staff, user.last_login,
                                                                                         sep=sep))
        else:
            print(f"id{sep}user{sep}actif{sep}dernière connexion")
            for user in q:
                print(
                    f"{user.pk}{sep}{user.username}{sep}{'actif' if user.is_active else 'inactif'}{sep}{user.last_login}"
                )
