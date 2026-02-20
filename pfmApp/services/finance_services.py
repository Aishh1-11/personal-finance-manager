
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

    # -------------------------------
    # DEEP BEHAVIORAL ANALYSIS
    # -------------------------------

    income = total_income  # use correct variable

    if income > 0:
        needs_ratio = (expense_needs / income) * Decimal('100')
        wants_ratio = (expense_wants / income) * Decimal('100')
        growth_ratio = (expense_growth / income) * Decimal('100')
        savings_ratio = (monthly_total_savings / income) * Decimal('100')
    else:
        needs_ratio = wants_ratio = growth_ratio = savings_ratio = Decimal('0')

    guidance_messages = []

    # 1️⃣ Needs Evaluation
    if needs_ratio > Decimal('60'):
        guidance_messages.append(
            "Your essential expenses are consuming a large portion of income. Review fixed costs."
        )
    elif needs_ratio < Decimal('40'):
        guidance_messages.append(
            "Your essential spending is well controlled."
        )

    # 2️⃣ Wants Evaluation
    if wants_ratio > Decimal('30'):
        guidance_messages.append(
            "Discretionary spending is high. Reducing wants could improve savings."
        )
    elif wants_ratio < Decimal('20'):
        guidance_messages.append(
            "Your discretionary spending is balanced."
        )

    # 3️⃣ Growth Spending (Positive Reinforcement)
    if growth_ratio > Decimal('10'):
        guidance_messages.append(
            "Excellent! Spending on growth improves long-term earning potential."
        )

    # 4️⃣ Savings Evaluation
    if savings_ratio >= Decimal('30'):
        guidance_messages.append(
            "Strong savings discipline. You're building financial security."
        )
    elif savings_ratio >= Decimal('15'):
        guidance_messages.append(
            "Moderate savings. Increasing it slightly would improve resilience."
        )
    else:
        guidance_messages.append(
            "Savings rate is low. Prioritize paying yourself first."
        )

    # 5️⃣ Commitment Safety Check
    if spendable_amount < 0:
        guidance_messages.append(
            "Warning: After commitments, your finances are in deficit."
        )

    # Combine into readable paragraph
    detailed_guidance = " ".join(guidance_messages)


    num_days = calendar.monthrange(year, month)[1]
    daily_dates = [date(year, month, day) for day in range(1, num_days + 1)]

    daily_income = []
    daily_expense = []

    cumulative_income = Decimal('0')
    cumulative_expense = Decimal('0')

    for day in daily_dates:
        day_income = IncomeDb.objects.filter(user=user, date=day).aggregate(total=Sum('amount'))['total'] or Decimal(
            '0')
        day_expense = ExpenseDb.objects.filter(user=user, date=day).aggregate(total=Sum('amount'))['total'] or Decimal(
            '0')
        cumulative_income += day_income
        cumulative_expense += day_expense

        # append cumulative balance after each day
        daily_income.append(float(cumulative_income))
        daily_expense.append(float(cumulative_expense))

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
        },

        "time_series":{
        "dates": [d.strftime("%d %b") for d in daily_dates],
        "daily_income": daily_income,
        "daily_expense": daily_expense
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
        "detailed_guidance": detailed_guidance,
        "needs_ratio": needs_ratio,
        "wants_ratio": wants_ratio,
        "growth_ratio": growth_ratio,
        "savings_ratio": savings_ratio,
        "daily_dates": [d.strftime("%d %b") for d in daily_dates],
        "daily_income": daily_income,
        "daily_expense": daily_expense
    }




def get_upcoming_bills(user, days_ahead=7, limit=3):
    today = now().date()

    commitments = CommitmentDb.objects.filter(user=user, active=True)

    upcoming_list = []

    for c in commitments:
        # Calculate the due date this month
        try:
            due_date_this_month = date(today.year, today.month, c.due_day)
        except ValueError:
            # For example, Feb 30 -> fallback to last day of month
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            due_date_this_month = date(today.year, today.month, last_day)

        # Overdue first
        if c.is_unpaid() and due_date_this_month < today:
            upcoming_list.append((c, 'overdue'))
        # Due within next 'days_ahead'
        elif c.is_unpaid() and today <= due_date_this_month <= today + timedelta(days=days_ahead):
            upcoming_list.append((c, 'upcoming'))

    # Sort: overdue first, then by due date
    upcoming_list.sort(key=lambda x: (x[1] != 'overdue', x[0].due_day))

    # Return only the commitment objects
    return [c for c, status in upcoming_list][:limit]



# when the commitments added to the expnse it should not be editable or deletable, and the commiments details are editable


