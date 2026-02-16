
from pfmApp.models import IncomeDb, ExpenseDb, SavingsDb, CommitmentDb
from django.utils.timezone import now
from decimal import Decimal
from django.db.models import Sum

def get_monthly_financial_summary(user, month=None, year=None):
    today = now()
    month = month or today.month
    year  = year or today.year

    # income
    total_income = IncomeDb.objects.filter(
        user=user, date__month=month, date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # expense
    total_expense = ExpenseDb.objects.filter(
        user=user, date__month=month, date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # savings
    monthly_total_savings = SavingsDb.objects.filter(
        user=user, date__month=month, date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    balance = total_income - total_expense - monthly_total_savings

    # commitments
    remaining_commitments = sum(
        c.amount for c in CommitmentDb.objects.filter(user=user, active=True)
        if not c.is_paid_this_month()
    )

    spendable_amount = balance - remaining_commitments

    # category-wise
    cumulative_safety = SavingsDb.objects.filter(user=user, category='safety').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    cumulative_retirement = SavingsDb.objects.filter(user=user, category='future_freedom').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    cumulative_goal = SavingsDb.objects.filter(user=user, category='goal').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    cumulative_investment = SavingsDb.objects.filter(user=user, category='investment').aggregate(total=Sum('amount'))['total'] or Decimal('0')



    #monthly
    monthly_safety = SavingsDb.objects.filter(user=user,category='safety', date__month = month, date__year = year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    monthly_retirement = SavingsDb.objects.filter(user=user,category="future_freedom", date__month= month, date__year = year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    monthly_investment = SavingsDb.objects.filter(user=user,category='investment').aggregate(total=Sum("amount"))['total'] or Decimal("0")

    # expense
    expense_needs = ExpenseDb.objects.filter(
        user=user, category='needs', date__month=month, date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    expense_wants = ExpenseDb.objects.filter(
        user=user, category='wants', date__month=month, date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    expense_growth = ExpenseDb.objects.filter(
        user=user, category='growth', date__month=month, date__year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')



    #chart data
    savings_investments = monthly_investment
    savings_future = monthly_retirement
    savings_safety = monthly_safety

    chart_data = {
        "outer":{
            "Expense": float(total_expense),
            "Savings":float(monthly_total_savings),
            "Balance": float(balance),

        },

        "expense_inner":{
            "Needs":float(expense_needs),
            "Wants":float(expense_wants),
            "Growth":float(expense_growth)
        },

        "savings_inner":{
            "Investments":float(savings_investments),
            "Future_Freedom":float(savings_future),
            "Safety":float(savings_safety),
        }
    }

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "remaining_commitments": remaining_commitments,
        "spendable_amount": spendable_amount,
        "cumulative_safety": cumulative_safety,
        "cumulative_retirement": cumulative_retirement,
        "cumulative_goal": cumulative_goal,
        "cumulative_investment": cumulative_investment,
        "monthly_total_savings": monthly_total_savings,
        "monthly_safety":monthly_safety,
        "monthly_retirement":monthly_retirement,
        "monthly_investment":monthly_investment,
        "chart_data": chart_data,
    }
