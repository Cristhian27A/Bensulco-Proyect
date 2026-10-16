"""Crea un superusuario inicial para el sistema de facturacion.

    python manage.py create_superuser

Este comando facilita la creacion del primer usuario del sistema,
usando valores predeterminados o argumentos de linea de comandos.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Crea un superusuario inicial para el sistema de facturacion."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="Nombre de usuario (default: admin)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="Contraseña (default: admin123)",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="admin@ejemplo.com",
            help="Correo electronico (default: admin@ejemplo.com)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"El usuario '{username}' ya existe. No se creara uno nuevo."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario creado exitosamente:\n"
                f"  Usuario: {username}\n"
                f"  Contraseña: {password}\n"
                f"  Email: {email}\n\n"
                f"Por favor, cambie la contraseña despues del primer inicio de sesion."
            )
        )
