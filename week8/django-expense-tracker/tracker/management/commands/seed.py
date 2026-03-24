from django.core.management.base import BaseCommand

from tracker.models import Transaction

SEED_DATA = [
    {"type": "expense", "category": "식비", "amount": 15000, "description": "점심 김치찌개", "date": "2026-03-01"},
    {"type": "expense", "category": "교통", "amount": 3000, "description": "버스비", "date": "2026-03-02"},
    {"type": "expense", "category": "쇼핑", "amount": 45000, "description": "운동화", "date": "2026-03-05"},
    {"type": "income", "category": "급여", "amount": 3500000, "description": "3월 급여", "date": "2026-03-10"},
    {"type": "expense", "category": "여가", "amount": 12000, "description": "영화 관람", "date": "2026-03-12"},
    {"type": "expense", "category": "주거", "amount": 500000, "description": "월세", "date": "2026-03-15"},
    {"type": "expense", "category": "식비", "amount": 8000, "description": "저녁 국밥", "date": "2026-03-18"},
    {"type": "income", "category": "용돈", "amount": 100000, "description": "부모님 용돈", "date": "2026-03-20"},
    {"type": "expense", "category": "교통", "amount": 55000, "description": "교통카드 충전", "date": "2026-02-05"},
    {"type": "expense", "category": "식비", "amount": 25000, "description": "회식", "date": "2026-02-10"},
    {"type": "income", "category": "급여", "amount": 3500000, "description": "2월 급여", "date": "2026-02-10"},
    {"type": "expense", "category": "쇼핑", "amount": 32000, "description": "책 구매", "date": "2026-02-15"},
    {"type": "expense", "category": "여가", "amount": 20000, "description": "카페", "date": "2026-02-20"},
]


class Command(BaseCommand):
    help = "Seed the database with sample transactions"

    def handle(self, *args, **options):
        Transaction.objects.all().delete()
        for item in SEED_DATA:
            Transaction.objects.create(**item)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(SEED_DATA)} transactions"))
