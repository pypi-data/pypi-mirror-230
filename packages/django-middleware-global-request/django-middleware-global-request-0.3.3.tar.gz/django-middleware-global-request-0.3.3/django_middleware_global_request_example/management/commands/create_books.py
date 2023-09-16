import uuid

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from django_middleware_global_request_example.models import Book
from django_middleware_global_request import GlobalRequest


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--number", type=int, default=10)

    def handle(self, *args, **options):
        number = options["number"]

        User = get_user_model()
        admin = User()
        admin.username = "admin" + uuid.uuid4().hex
        admin.set_password(uuid.uuid4().hex)
        admin.is_active = True
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        with GlobalRequest(user=admin):
            for i in range(number):
                book = Book(name="book{idx}".format(idx=i + 1))
                book.save()
                print(i, book.name, book.author.username)
                assert book.author.pk == admin.pk
