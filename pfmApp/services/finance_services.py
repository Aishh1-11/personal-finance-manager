
from pfmApp.models import IncomeDb, ExpenseDb, SavingsDb, CommitmentDb
from django.utils.timezone import now
from decimal import Decimal
from django.db.models import Sum
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
        "detailed_guidance": detailed_guidance,
        "needs_ratio": needs_ratio,
        "wants_ratio": wants_ratio,
        "growth_ratio": growth_ratio,
        "savings_ratio": savings_ratio,
    }





   #  user = request.user
   #  today = now()
   #  current_month = today.month
   #  current_year = today.year
   #  current_month_name = today.strftime("%B")
   #
   #
   #  # income total
   #  result  = IncomeDb.objects.filter(
   #      user=user,
   #      date__month=current_month,
   #      date__year=current_year,
   #  ).aggregate(total = Sum('amount'))
   #
   #  total_income = result['total'] if result['total'] is not None else Decimal('0')
   #
   #
   #  # expense total
   #
   #  result = ExpenseDb.objects.filter(user=user,date__month=current_month,date__year=current_year).aggregate(total=Sum("amount"))
   #  total_expense = result['total'] if result['total'] is not None else Decimal("0")
   #
   #
   # # savings total month
   #  monthly_total_savings = SavingsDb.objects.filter(user=user,date__month = current_month,date__year = current_year ).aggregate(total=Sum("amount"))['total'] or Decimal('0')
   #
   #  cumulative_savings = SavingsDb.objects.filter(user=user).aggregate(total = Sum('amount'))['total'] or Decimal("0")
   #
   #
   #
   #  balance = total_income-total_expense-monthly_total_savings  # can be neg #show warning
   #
   #
   #
   #
   #
   #
   #  # commitments_total
   #
   #  result = CommitmentDb.objects.filter(user=user,active=True).aggregate(total=Sum('amount'))
   #  total_commitment = result['total'] if result['total'] is not None else Decimal('0')
   #
   #  remaining_commitments = Decimal('0')
   #
   #  for c in CommitmentDb.objects.filter(active=True,user=user):
   #      if not c.is_paid_this_month():
   #          remaining_commitments +=c.amount
   #
   #
   #  spendable_amount = balance-remaining_commitments # can be neg # show warning
   #
   #
   #  # safety,growth freedom fund
   #
   #  cumulative_safety = SavingsDb.objects.filter(user=user,category="safety").aggregate(total=Sum('amount'))['total'] or Decimal('0')
   #
   #  cumulative_freedom = SavingsDb.objects.filter(user=user, category="freedom").aggregate(total=Sum('amount'))[
   #                          'total'] or Decimal('0')
   #
   #  cumulative_growth = ExpenseDb.objects.filter(user=user, category="Growth").aggregate(total=Sum('amount'))[
   #                          'total'] or Decimal('0')
   #
   #
   #  #monthly safety,growth freedom fund
   #
   #  monthly_safety = SavingsDb.objects.filter(user=user,category="safety",date__month=current_month,date__year=current_year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
   #
   #  monthly_freedom = SavingsDb.objects.filter(user=user,category="freedom",date__month=current_month,date__year=current_year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
   #
   #  monthly_growth = ExpenseDb.objects.filter(user=user,category="Growth",date__month=current_month,date__year=current_year).aggregate(total=Sum('amount'))['total'] or Decimal('0')
