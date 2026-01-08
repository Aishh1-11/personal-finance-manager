from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from pfmApp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date
from django.db.models import Sum
from django.utils.timezone import now


# Create your views here.
def dashboard(request):
    user = request.user
    today = now()
    current_month = today.month
    current_year = today.year
    current_month_name = today.strftime("%B")

    total_income = IncomeDb.objects.filter(
        User=user,
        Date__month=current_month,
        Date__year=current_year,
    ).aggregate(Sum('Amount'))['Amount__sum'] or 0


    return render(request,"dashboard.html",{"user":user,"total_income": total_income,"current_month_name":current_month_name})

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

def add_income(request):
    return render(request,"add_income.html",{'today':date.today()})

@login_required
def save_income(request):

    if request.method == "POST":

        amnt = request.POST.get("amount")
        src = request.POST.get("source")
        date_input = request.POST.get("date")
        note = request.POST.get("note")

        obj = IncomeDb(User=request.user,Amount=amnt,Income_source=src,Date=date_input,Note=note)
        obj.save()

    messages.success(request, "Income added successfully.")
    return redirect('view_income')

def view_income(request):
    income = IncomeDb.objects.filter(User=request.user)

    return render(request,"view_income.html",{"income":income})

@login_required
def edit_income(request,income_id):
    income = IncomeDb.objects.get(id=income_id,User=request.user)
    return render(request,"edit_income.html",{"income":income})

def update_income(request,income_id):

    if request.method=="POST":
        amnt = request.POST.get("amount")
        src = request.POST.get("source")
        date = request.POST.get("date")
        note = request.POST.get("note")

        obj = IncomeDb.objects.filter(id=income_id,User=request.user).update(Amount=amnt,Income_source=src,Date=date,Note=note)
    return redirect(view_income)

@login_required
def delete_income(request,income_id):

    income = get_object_or_404(IncomeDb, id=income_id, User=request.user)

    if request.method == "POST":
        income.delete()
        return redirect("view_income")

    return redirect("view_income")

# ****************************************************************************************************************************************


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

        obj = ExpenseDb(User=request.user,Amount=amnt,Expense_title=title,Date=date,Note=note,Category=cat)
        obj.save()


    return redirect('add_expense')


def view_expense(request):

    expense = ExpenseDb.objects.filter(User=request.user)
    return render(request,"view_expense.html",{"expense":expense})

def edit_expense(request,expense_id):

    expense = ExpenseDb.objects.get(User=request.user,id=expense_id)
    return render(request,"edit_expense.html",{"expense":expense})

def update_expense(request,expense_id):

    if request.method == "POST":

        amnt = request.POST.get("amount")
        title = request.POST.get("title")
        date = request.POST.get("date")
        note = request.POST.get("note")
        cat = request.POST.get("category")

        ExpenseDb.objects.filter(id=expense_id).update(Amount=amnt,Expense_title=title,Date=date,Note=note,Category=cat)
        return redirect(view_expense)

def delete_expense(request,expense_id):

    expense = get_object_or_404(ExpenseDb,User=request.user,id=expense_id)
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
    commitments = CommitmentDb.objects.all()
    return render(request,"view_commitments.html",{"commitments":commitments})

def edit_commitment(request,commitment_id):
    commitment = CommitmentDb.objects.get(id=commitment_id)
    return render(request,"edit_commitment.html",{"commitment":commitment})

def update_commitment(request,commitment_id):
    if request.method == "POST":

        title = request.POST.get("title")
        amt = request.POST.get("amount")
        due = request.POST.get("due_day")
        is_r = request.POST.get("is_recurring")
        note = request.POST.get("note")

        CommitmentDb.objects.filter(id=commitment_id).update(user=request.user,title=title,amount=amt,due_day=due,is_recurring=is_r,note=note)

    return redirect("view_commitment")

def delete_commitment(request,commitment_id):

    commitment = get_object_or_404(CommitmentDb,user=request.user,id=commitment_id)
    if request.method == "POST":
        commitment.delete()
        return redirect("view_commitment")

    return redirect("view_commitment")

def mark_commitment_paid(request,commitment_id):
    commitment = get_object_or_404(CommitmentDb,id=commitment_id,user=request.user)
    success = commitment.mark_as_paid()

    if success :
        messages.success(request,"commitment masked as paid and expense created")
    else:
        messages.warning(request,"commitment already paid this month")



    return redirect("view_commitment")



