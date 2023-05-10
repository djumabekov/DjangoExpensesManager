import random
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("agg")
from expenses import settings

from typing import Optional

from django.core.paginator import Paginator
from django.db.models import Sum, Avg

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from app.models import Transaction


def index(request):
    if request.user.is_authenticated:
        return redirect('/account')
    else:
        return render(request, 'index.html')


def account(request, transaction_type=""):
    user = request.user
    if not user.is_authenticated:
        return redirect("/")

    # Берём поиск из запроса и записываем в переменную search
    search = request.GET.get("search", "")
    message = request.GET.get("message", "")

    # Сортируем транзакции в обратном порядке
    transactions = Transaction.objects.filter(user=user).order_by("-id")
    if transaction_type == "expenses":
        transactions = transactions.filter(amount__lt=0)
    if transaction_type == "incomes":
        transactions = transactions.filter(amount__gt=0)
    # Если мы что-то ищем (search не пустой), то применяем фильтры
    # Здесь icontains значит, что мы ищем внутри строки, а буква i вначале делает
    # поиск независимым от регистра (строчные или прописные буквы)
    if search != "":
        transactions = transactions.filter(description__icontains=search)

    # Добавляем фильтр по расходам и доходам
    if transaction_type == "expenses":
        transactions = transactions.filter(amount__lt=0)
    if transaction_type == "incomes":
        transactions = transactions.filter(amount__gt=0)
    report = ""
    if transaction_type == "report":
        filename = f"{user.id}_report.png"
        report = f"/media/{filename}"

    if message == "insufficient":
        message = "Недостаточно средств"

    total = transactions.aggregate(Sum("amount"))["amount__sum"]
    if total is None:
        total = 0
    agg_avg = transactions.aggregate(Avg("amount"))["amount__avg"]
    if agg_avg is not None:
        avg = round(agg_avg)
    else:
        avg = 0

    paginator = Paginator(transactions, 10)  # 5 - размер страницы

    page: int = 1
    if request.GET.get("page"):
        page = int(request.GET.get("page"))

    page_obj = paginator.get_page(page)
    transactions = page_obj.object_list

    html_file = 'account.html'

    if request.GET.get("ajax", "") == "1":
        html_file = "table.html"

    return render(request, html_file, {
        'user': user,
        "transactions": transactions,
        "transaction_type": transaction_type,  # Добавляем тип транзакции
        "number_of_pages": paginator.num_pages,
        "pages": paginator.page_range,  # range(1, paginator.num_pages + 1),
        "current_page": page,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "previous_page": page - 1,  # page_obj.previous_page_number(),
        "next_page": page + 1,  # page_obj.next_page_number(),
        "search": search,  # <--- передаём значение в HTML
        "total": total,
        "avg": avg,
        "message": message,
        "report": report,
    })

def delete_view(request: HttpRequest, transaction_id: int) -> HttpResponse:
    Transaction.objects.filter(id=transaction_id).filter(user=request.user).delete()
    return redirect("/")


def create_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        transaction: Optional[Transaction] = None
        if request.POST.get("type", "") == "expense":
            total = Transaction.objects.filter(user=user).aggregate(Sum("amount"))["amount__sum"]
            if total is None:
                total = 0
            if total < abs(int(request.POST.get("amount", 0))):
                return redirect("/account/?message=insufficient")
            transaction = Transaction.objects.create(
                user=user,
                description=request.POST.get("description", ""),
                amount=-abs(int(request.POST.get("amount", 0))),
            )
        if request.POST.get("type", "") == "income":
            transaction = Transaction.objects.create(
                user=user,
                description=request.POST.get("description", ""),
                amount=abs(int(request.POST.get("amount", 0))),
            )
        if transaction is not None:
            if request.FILES.get("evidence", None):
                transaction.evidence = request.FILES["evidence"]
                transaction.save()
        return redirect("/")

    raise NotImplementedError


def edit_view(request: HttpRequest, transaction_id: int) -> HttpResponse:
    transaction = Transaction.objects.filter(id=transaction_id).filter(user=request.user).first()

    if request.method == "POST":
        transaction.description = request.POST.get("description", "")
        if request.POST.get("type", "") == "expense":
            transaction.amount = -abs(int(request.POST.get("amount", 0)))
        if request.POST.get("type", "") == "income":
            transaction.amount = abs(int(request.POST.get("amount", 0)))
        if request.FILES.get("evidence", None):
            transaction.evidence = request.FILES["evidence"]
        transaction.save()
        return redirect("/")

    raise NotImplementedError


def add10(request):
    user = request.user
    if not user.is_authenticated: return redirect("/")
    random_descriptions_expenses = [
        "Bought a new car",
        "Bought a new house",
        "Bought a new phone",
        "Bought a new computer",
        "Bought a new TV",
        "Bought a new fridge",
        "Bought a new microwave",
        "Bought a new toaster",
    ]

    random_descriptions_income = [
        "Got salary",
        "Got a bonus",
        "Got a gift",
        "Got a lottery",
    ]

    for i in range(10):
        Transaction.objects.create(
            user=user,
            description=random.choice(random_descriptions_expenses),
            amount=-abs(random.randint(100, 1000)),
        )
        for i in range(5):
            Transaction.objects.create(
                user=user,
                description=random.choice(random_descriptions_income),
                amount=abs(random.randint(1000, 5000)),
            )

        return redirect("/")

