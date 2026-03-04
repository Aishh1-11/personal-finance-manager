
from pfmApp.models import IncomeDb, ExpenseDb, SavingsDb, CommitmentDb
from django.utils.timezone import now
from decimal import Decimal
from django.db.models import Sum
import calendar
from datetime import date,timedelta
import json
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
        c.amount for c in CommitmentDb.objects.filter(user=user, active=True) if not c.is_paid_this_month()
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
    monthly_investment = SavingsDb.objects.filter(user=user,category='investment',date__month= month, date__year = year).aggregate(total=Sum("amount"))['total'] or Decimal("0")

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

    expense_commitments = ExpenseDb.objects.filter(user = user,date__year = year, date__month = month).aggregate(total = Sum('amount'))['total'] or Decimal('0')
    total_commitments = expense_commitments













# financial insight **************************************************************************************************************************



    income = total_income

    if income > 0:
        needs_ratio = (expense_needs / income) * Decimal('100')
        wants_ratio = (expense_wants / income) * Decimal('100')
        growth_ratio = (expense_growth / income) * Decimal('100')

        savings_ratio = (monthly_total_savings / income) * Decimal('100')

        balance_ratio = (balance / income) * Decimal('100')
        commitment_ratio = (expense_commitments / income) * Decimal('100')
    else:
        needs_ratio = wants_ratio = growth_ratio = savings_ratio = balance_ratio = commitment_ratio = Decimal('0')


    guidance_messages = []

   # checking finanacial stabilityy ***************************************************************************


    if spendable_amount < 0:
        guidance_messages.append(
            "⚠️ You Does not have enough spendable amount. "
        )
    elif balance_ratio < Decimal('10'):
        guidance_messages.append(
            "Your remaining balance is very low. Avoid additional discretionary expenses."
        )
    elif balance_ratio > Decimal('30'):
        guidance_messages.append(
            "You have healthy leftover balance. Consider increasing savings or investing."
        )

    # 1 Needs
    if needs_ratio > Decimal('60'):
        guidance_messages.append(
            "Essential expenses are consuming most of your income."
        )
    elif needs_ratio < Decimal('40'):
        guidance_messages.append(
            "Essential spending is efficiently managed."
        )

    #  Wants
    if wants_ratio > Decimal('30'):
        guidance_messages.append(
            "Discretionary spending is high. Reducing wants can improve wealth building."
        )
    elif wants_ratio < Decimal('20'):
        guidance_messages.append(
            "Discretionary spending is controlled."
        )

    #  Growth
    if growth_ratio < Decimal('5'):
        guidance_messages.append(
            "Consider investing in skill growth or learning to increase future income."
        )
    elif growth_ratio >= Decimal('10'):
        guidance_messages.append(
            "Excellent investment in growth. This builds long-term earning power."
        )

    #  Savings
    if savings_ratio >= Decimal('30'):
        guidance_messages.append(
            "Outstanding savings discipline. Financial independence path is strong."
        )
    elif savings_ratio >= Decimal('15'):
        guidance_messages.append(
            "Good savings rate. Increasing slightly will improve resilience."
        )
    else:
        guidance_messages.append(
            "Savings rate is low. Try allocating a fixed portion at the start of the month."
        )


    if commitment_ratio > Decimal('40'):
        guidance_messages.append(
            "High commitment load. Avoid taking new fixed obligations."
        )

    detailed_guidance = " ".join(guidance_messages)

    # ***************************************************************************



    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    income_data = (
        IncomeDb.objects
        .filter(user=user, date__month=month, date__year=year)
        .values('date')
        .annotate(total=Sum('amount'))
    )

    income_dict = {i['date']: float(i['total']) for i in income_data}

    daily_dates = []
    daily_income = []

    running_total = 0
    current = start_date

    while current <= end_date:
        daily_dates.append(current.strftime("%d %b"))

        if current in income_dict:
            running_total += income_dict[current]

        daily_income.append(running_total)

        current += timedelta(days=1)





#***************************************************************************************************

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
            "Growth":float(expense_growth),
            "Commitments":float(expense_commitments)

        },

        "savings_inner":{
            "Investments":float(savings_investments),
            "Future_Freedom":float(savings_future),
            "Safety":float(savings_safety),
        },



        "time_series": {
            "dates": daily_dates,
            "daily_income": daily_income
        }
    }





    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "total_commitments": total_commitments,
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
        "detailed_guidance": detailed_guidance,
        "needs_ratio": needs_ratio,
        "wants_ratio": wants_ratio,
        "growth_ratio": growth_ratio,
        "savings_ratio": savings_ratio,

    }



def upcoming_commitment(user):
    commitments = CommitmentDb.objects.filter(user=user)

    overdue = [c for c in commitments if c.is_overdue()]
    unpaid = [c for c in commitments if c.is_unpaid() and not c.is_overdue()]

    re = overdue + unpaid

    return re[:3]





# when the commitments added to the expnse it should not be editable or deletable, and the commiments details are editable


