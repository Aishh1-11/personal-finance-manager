from django.urls import path
from pfmApp import views

urlpatterns=[
    path('home/',views.home,name="home"),
    path("dashboard/",views.dashboard,name="dashboard"),

    path("user_registration_page/",views.user_registration_page,name="user_registration_page"),
    path("user_registration/",views.user_registration,name="user_registration"),

    path("login_page/",views.login_page,name="login_page"),
    path("user_login/",views.user_login,name="user_login"),
    path("user_logout/",views.user_logout,name="user_logout"),


    path("add_income/",views.add_income,name="add_income"),
    path("save_income/",views.save_income,name="save_income"),
    path("view_income/",views.view_income,name="view_income"),
    path("edit_income/<int:income_id>/",views.edit_income,name="edit_income"),
    path("update_income/<int:income_id>/",views.update_income,name="update_income"),
    path("delete_income/<int:income_id>/",views.delete_income,name="delete_income"),

    path("add_expense/",views.add_expense,name="add_expense"),
    path("save_expense/",views.save_expense,name="save_expense"),
    path("view_expense/",views.view_expense,name="view_expense"),
    path("edit_expense/<int:expense_id>/",views.edit_expense,name="edit_expense"),
    path("update_expense/<int:expense_id>/",views.update_expense,name="update_expense"),
    path("delete_expense/<int:expense_id>/",views.delete_expense,name="delete_expense"),


    path("add_commitment/",views.add_commitment,name="add_commitment"),
    path("save_commitment/",views.save_commitment,name="save_commitment"),
    path("view_commitment/",views.view_commitment,name="view_commitment"),
    path("edit_commitment/<int:commitment_id>/",views.edit_commitment,name="edit_commitment"),
    path("update_commitment/<int:commitment_id>/",views.update_commitment,name="update_commitment"),



    path("mark_commitment_paid/<int:commitment_id>/",views.mark_commitment_paid,name="mark_commitment_paid"),



    path("add_savings/", views.add_savings, name="add_savings"),
    path("save_savings/", views.save_savings, name="save_savings"),
    path("view_savings/", views.view_savings, name="view_savings"),
    path("edit_savings/<int:saving_id>/", views.edit_savings, name="edit_savings"),
    path("update_savings/<int:saving_id>/", views.update_savings, name="update_savings"),
    path("delete_savings/<int:saving_id>/", views.delete_savings, name="delete_savings"),
    path("withdraw_savings/", views.withdraw_savings_page, name="withdraw_savings"),
    path("save_withdrawal/", views.save_withdrawal, name="save_withdrawal"),

    path("budget/",views.budget_page, name="budget"),




]