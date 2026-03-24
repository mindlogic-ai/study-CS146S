import json
from datetime import date

from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Transaction

EXPENSE_CATEGORIES = ["식비", "교통", "쇼핑", "주거", "여가", "기타"]
INCOME_CATEGORIES = ["급여", "용돈", "기타수입"]


@csrf_exempt
def transactions(request):
    if request.method == "GET":
        qs = Transaction.objects.all()
        month = request.GET.get("month")  # YYYY-MM
        category = request.GET.get("category")
        tx_type = request.GET.get("type")
        if month:
            year, m = month.split("-")
            qs = qs.filter(date__year=int(year), date__month=int(m))
        if category:
            qs = qs.filter(category=category)
        if tx_type:
            qs = qs.filter(type=tx_type)
        data = list(
            qs.values("id", "type", "category", "amount", "description", "date", "created_at")
        )
        for d in data:
            d["date"] = d["date"].isoformat()
            d["created_at"] = d["created_at"].isoformat()
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        body = json.loads(request.body)
        tx = Transaction.objects.create(
            type=body["type"],
            category=body["category"],
            amount=body["amount"],
            description=body.get("description", ""),
            date=body["date"],
        )
        return JsonResponse({"id": tx.id}, status=201)


@csrf_exempt
def transaction_detail(request, pk):
    try:
        tx = Transaction.objects.get(pk=pk)
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method == "PATCH":
        body = json.loads(request.body)
        for field in ["type", "category", "amount", "description", "date"]:
            if field in body:
                setattr(tx, field, body[field])
        tx.save()
        return JsonResponse({"id": tx.id})

    if request.method == "DELETE":
        tx.delete()
        return JsonResponse({"ok": True})


def summary(request):
    month = request.GET.get("month")
    if not month:
        today = date.today()
        month = today.strftime("%Y-%m")
    year, m = month.split("-")
    qs = Transaction.objects.filter(date__year=int(year), date__month=int(m))

    total_income = qs.filter(type="income").aggregate(s=Sum("amount"))["s"] or 0
    total_expense = qs.filter(type="expense").aggregate(s=Sum("amount"))["s"] or 0
    by_category = list(
        qs.values("category").annotate(total=Sum("amount")).order_by("-total")
    )
    return JsonResponse(
        {
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "by_category": by_category,
        }
    )


def categories(request):
    return JsonResponse(
        {
            "expense": EXPENSE_CATEGORIES,
            "income": INCOME_CATEGORIES,
        }
    )
