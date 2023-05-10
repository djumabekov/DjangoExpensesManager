from django.core.management.base import BaseCommand
from app.models import Transaction, User
import matplotlib.pyplot as plt
from expenses import settings
import time


class Command(BaseCommand):
    help = "Generate graphs"

    def create_graph(self, user: User):
        filename = f"{user.id}_report.png"
        all_transactions = Transaction.objects.filter(user=user).order_by("id")
        balance = 0
        chart = []
        for transaction in all_transactions:
            balance += transaction.amount
            chart.append(balance)
        plt.clf()
        plt.figure(figsize=(12, 4))
        plt.plot(chart)
        plt.savefig(f"{settings.MEDIA_ROOT}/{filename}")

    def handle(self, *args, **options):
        while True:
            for user in User.objects.all():
                self.create_graph(user)

            self.stdout.write(
                self.style.SUCCESS("graphs created")
            )
            time.sleep(5)