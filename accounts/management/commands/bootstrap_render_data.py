from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Loads the checked-in Render seed data when the database is empty."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reload the seed fixture even if users already exist.",
        )

    def handle(self, *args, **options):
        fixture_path = (
            Path(__file__).resolve().parents[3]
            / "seago"
            / "fixtures"
            / "render_seed.json"
        )
        user_model = get_user_model()
        user_count = user_model.objects.count()

        if user_count and not options["force"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seed skipped: database already contains {user_count} user(s)."
                )
            )
            return

        if not fixture_path.exists():
            raise CommandError(f"Seed fixture not found: {fixture_path}")

        self.stdout.write(f"Loading Render seed data from {fixture_path}...")
        call_command("loaddata", str(fixture_path))
        self.stdout.write(self.style.SUCCESS("Render seed data loaded successfully."))
