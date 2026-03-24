from django.db import models


class Transaction(models.Model):
    TRANSACTION_TYPES = [("income", "Income"), ("expense", "Expense")]

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=200, blank=True, default="")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
