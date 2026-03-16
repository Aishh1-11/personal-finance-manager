from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from datetime import date, timedelta
import calendar
from django.utils.timezone import now



# Create your models here.
class IncomeDb(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(db_index=True)
    income_source = models.CharField(max_length=100)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user}-{self.income_source}"

class ExpenseDb(models.Model):

    EXPENSE_CATEGORIES = [
        ('needs','Needs'),
        ('wants', 'Wants'),
        ('growth', 'Growth'),
        ('commitment', 'Commitment')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField( max_length=50, choices = EXPENSE_CATEGORIES)
    note = models.TextField(blank=True, null=True)
    sub_category = models.ForeignKey('ExpenseSubCategory', on_delete=models.SET_NULL, null=True, blank=True,related_name='expenses')

    def __str__(self):
        return f"{self.user}={self.expense_title}"

class ExpenseSubCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    period = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class CommitmentDb(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    due_day=models.IntegerField()
    is_recurring = models.BooleanField(default=True,null=True,blank=True)
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

            ExpenseDb.objects.create(user=self.user,expense_title=self.title,amount=self.amount,date=self.last_paid_date,category="commitment")

        return True

    def is_upcoming(self, days_ahead=7):
        today = now().date()
        end_date = today + timedelta(days=days_ahead)

        try:
            due_date = date(today.year, today.month, self.due_day)
        except ValueError:
            last_day = calendar.monthrange(today.year, today.month)[1]
            due_date = date(today.year, today.month, last_day)

        if not self.is_unpaid():
            return False

        return due_date <= end_date and self.is_unpaid()


class SavingsDb(models.Model):
    SAVING_CATEGORIES = [
        ('safety', 'Safety Fund'),
        ('future_freedom', 'Future Freedom'),
        ('goal', 'Goal Saving'),
        ('investment', 'Investment Fund')
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    category = models.CharField(max_length =50, choices = SAVING_CATEGORIES)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    date = models.DateField()
    note = models.CharField(max_length =500, blank = True, null = True)


class ProfileDb(models.Model)  :

    user = models.OneToOneField(User, on_delete = models.CASCADE)
    phone = models.IntegerField(null=True,blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/',null=True,blank=True)

    def __str__(self):
        return f"{self.user}"












