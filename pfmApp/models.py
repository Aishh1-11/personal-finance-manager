from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date


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
