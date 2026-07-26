import time
from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Waiting for database")
        db_conn = None
        while db_conn is None:
            try:
                db_conn = connection.cursor()
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second..")
                time.sleep(1)
