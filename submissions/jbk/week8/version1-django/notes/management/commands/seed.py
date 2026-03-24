from django.core.management.base import BaseCommand
from notes.models import ActionItem, Note


class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **options):
        Note.objects.all().delete()
        ActionItem.objects.all().delete()

        Note.objects.create(
            title="Welcome",
            content="This is a starter note. TODO: explore the app!",
        )
        Note.objects.create(
            title="Demo",
            content="Click around and add a note. Ship feature!",
        )
        ActionItem.objects.create(description="Try pre-commit", completed=False)
        ActionItem.objects.create(description="Run tests", completed=False)

        self.stdout.write(self.style.SUCCESS("Seeded 2 notes and 2 action items"))
