from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction


# Create your models here.
class IncomeDb(models.Model):

    User = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Date = models.DateField(db_index=True)
    Income_source = models.CharField(max_length=100)
    Note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.User}-{self.Income_source}"

class ExpenseDb(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Expense_title = models.CharField(max_length=100)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    Date = models.DateField()
    Category = models.CharField( max_length=50 )
    Note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.User}={self.Expense_title}"


class CommitmentDb(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    due_day=models.IntegerField()
    is_recurring = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)

    last_paid_date = models.DateField(null=True,blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['due_day','title']

    def __str__(self):
        return f"{self.user}={self.title}"


    def is_paid_this_month(self):
        if self.last_paid_date:
            return self.last_paid_date.month == timezone.now().month and self.last_paid_date.year == timezone.now().year

        return False

    def is_overdue(self):
        today = timezone.now().day
        if not self.is_paid_this_month() and today > self.due_day:
            return True
        else:
            return False


    def is_unpaid(self):
        return not self.is_paid_this_month()

    def mark_as_paid(self):
        if self.is_paid_this_month():
            return False

        with transaction.atomic():
            self.last_paid_date = timezone.now().date()
            self.save()

            ExpenseDb.objects.create(User=self.user,Expense_title=self.title,Amount=self.amount,Date=self.last_paid_date,Category="Commitment")

        return True










