from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Income(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    income_source = models.CharField(max_length=100)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.income_source} - {self.amount}"


