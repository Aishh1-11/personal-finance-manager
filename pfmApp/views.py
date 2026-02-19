from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.contrib.auth import authenticate,login,logout
from pfmApp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date
from django.db.models import Sum
from django.utils.timezone import now
from decimal import Decimal
from pfmApp.services.finance_services import get_monthly_financial_summary
import json

# Create your views here.
def dashboard(request):
    summary = get_monthly_financial_summary(request.user)


    context = {
        "summary": summary,
        "chart_data": json.dumps(summary["chart_data"]),
        "current_month_name": now().strftime("%B"),
    }

    return render(request, "dashboard.html", context)






#**************************************************************************************************************************************************************************

def user_registration_page(request):
    return render(request,"user_registration_page.html")

def login_page(request):
    return render(request,"login_page.html")

def user_registration(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")


        if password1 != password2:
            return render(request, "user_registration_page.html", {"error": "Passwords do not match"})


        if User.objects.filter(username=username).exists():
            return render(request, "user_registration_page.html", {"error": "Username already exists"})


        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login_page")

    return render(request, "user_registration_page.html")




def user_login(request):


    if request.method == "POST":


        uname = request.POST.get("username")
        pwd = request.POST.get("password")
        print("Username:", uname)

        user = authenticate(request, username=uname, password=pwd)

        if user is not None:

            login(request, user)
            return redirect("dashboard")


        return render(request, "login_page.html", {"error": "Invalid username or password"})

    return render(request, "login_page.html")


def user_logout(request):
    logout(request)
    return redirect("login_page")

# ****************************************************************************************************************************************
@login_required
def add_income(request):
    return render(request,"add_income.html",{'today':date.today()})

@login_required
def save_income(request):

    if request.method == "POST":

        amnt = request.POST.get("amount")
        src = request.POST.get("source")
        date_input = request.POST.get("date")
        note = request.POST.get("note")

        obj = IncomeDb(user=request.user,amount=amnt,income_source=src,date=date_input,note=note)
        obj.save()

    messages.success(request, "Income added successfully.")
    return redirect('view_income')
@login_required
def view_income(request):
    income = IncomeDb.objects.filter(user=request.user)

    return render(request,"view_income.html",{"income":income})


def edit_income(request,income_id):
    income = IncomeDb.objects.get(id=income_id,user=request.user)
    return render(request,"edit_income.html",{"income":income})


def update_income(request,income_id):

    if request.method=="POST":
        amnt = request.POST.get("amount")
        src = request.POST.get("source")
        date = request.POST.get("date")
        note = request.POST.get("note")

        obj = IncomeDb.objects.filter(id=income_id,user=request.user).update(amount=amnt,income_source=src,date=date,note=note)
    return redirect("view_income")

@login_required
def delete_income(request,income_id):

    income = get_object_or_404(IncomeDb, id=income_id, user=request.user)

    if request.method == "POST":
        income.delete()
        return redirect("view_income")

    return redirect("view_income")

# ****************************************************************************************************************************************

@login_required
def add_expense(request):
    return render(request,"add_expense.html",{'today':date.today()})

@login_required
def save_expense(request):

    if request.method == "POST":

        amnt = request.POST.get("amount")
        title = request.POST.get("title")
        date = request.POST.get("date")
        note = request.POST.get("note")
        cat = request.POST.get("category")

        obj = ExpenseDb(user=request.user,amount=amnt,expense_title=title,date=date,note=note,category=cat)
        obj.save()


    return redirect('add_expense')

@login_required
def view_expense(request):

    expense = ExpenseDb.objects.filter(user=request.user)
    return render(request,"view_expense.html",{"expense":expense})

def edit_expense(request,expense_id):

    expense = ExpenseDb.objects.get(user=request.user,id=expense_id)
    return render(request,"edit_expense.html",{"expense":expense})

def update_expense(request,expense_id):

    if request.method == "POST":

        amnt = request.POST.get("amount")
        title = request.POST.get("title")
        date = request.POST.get("date")
        note = request.POST.get("note")
        cat = request.POST.get("category")

        ExpenseDb.objects.filter(id=expense_id).update(amount=amnt,expense_title=title,date=date,note=note,category=cat)
        return redirect(view_expense)

def delete_expense(request,expense_id):

    expense = get_object_or_404(ExpenseDb,user=request.user,id=expense_id)
    if request.method=="POST":
        expense.delete()
        return redirect(view_expense)

    return redirect(view_income)
#***************************************************************************************************************************************************************************

def add_commitment(request):
    return render(request,"add_commitment.html")

def save_commitment(request):

    if request.method == "POST":

        title = request.POST.get("title")
        amt = request.POST.get("amount")
        due = request.POST.get("due_day")
        is_r = request.POST.get("is_recurring")
        note = request.POST.get("note")

        CommitmentDb.objects.create(user=request.user,title=title,amount=amt,due_day=due,is_recurring=is_r,note=note)

    return redirect("add_commitment")


def view_commitment(request):
    commitments = CommitmentDb.objects.filter(user=request.user)
    return render(request,"view_commitments.html",{"commitments":commitments})



def mark_commitment_paid(request,commitment_id):
    commitment = get_object_or_404(CommitmentDb,id=commitment_id,user=request.user)
    success = commitment.mark_as_paid()

    if success :
        messages.success(request,"commitment masked as paid and expense created")
    else:
        messages.warning(request,"commitment already paid this month")



    return redirect("view_commitment")




#*********************************************************************************************************************************************************

def add_savings(request):

    return render(request,"add_savings.html")

def save_savings(request):

    if request.method == "POST" :

        amnt = request.POST.get("amount")
        cat = request.POST.get("category")
        date = request.POST.get("date")
        note = request.POST.get("note")

        SavingsDb.objects.create(user = request.user, amount = amnt, category = cat, date = date, note = note)

    return redirect("add_savings")

def view_savings(request):

    savings = SavingsDb.objects.filter(user=request.user)
    return render(request,"view_savings.html",{"savings":savings})

def edit_savings(request, saving_id):

    savings = SavingsDb.objects.get(user = request.user,id = saving_id)
    return render(request, "edit_savings.html", {"savings":savings})

def update_savings(request, saving_id):
    if request.method == "POST":
        amount = request.POST.get("amount")
        cat = request.POST.get('category')
        date = request.POST.get("date")
        note = request.POST.get("note")

        SavingsDb.objects.filter(user = request.user, id = saving_id).update(amount = amount, category = cat, date = date, note = note)
    return redirect("view_savings")

def delete_savings(request, saving_id):

    saving = get_object_or_404(SavingsDb, user = request.user, id = saving_id)
    if request.method == "POST":
        saving.delete()

    return redirect("view_savings")

def withdraw_savings_page(request):

    return render(request,"withdraw_savings.html")


def save_withdrawal(request):

    if request.method == "POST":
        category = request.POST.get("category")
        withdraw_amount = Decimal(request.POST.get("amount"))
        date = request.POST.get("date")
        note = request.POST.get("note")

        current_balance = SavingsDb.objects.filter(user = request.user, category = category). aggregate(total = Sum("amount"))['total'] or Decimal('0')

        if withdraw_amount > current_balance:
            return redirect(reverse("view_savings") + "?error=insufficient")

        SavingsDb.objects.create(
            user=request.user,
            category=category,
            amount=-withdraw_amount,
            date=date,
            note=note or f"Withdraw from {category}"
        )

        messages.success(request, f"Successfully withdrew {withdraw_amount} from {category}.")
        return redirect('view_savings')

    return redirect("view_savings")




