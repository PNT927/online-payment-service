from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('send-payment/', views.send_payment, name='send_payment'),
    path('transactions/', views.transactions_history, name='transactions_history'),
    path('request-payment/', views.request_payment, name="request_payment"),
    path('requests/<int:request_id>/accept/', views.accept_request, name="accept_request"),
    path('requests/<int:request_id>/reject/', views.reject_request, name="reject_request"),


    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("staff/accounts/", views.admin_accounts, name="admin_accounts"),
    path("staff/transactions/", views.admin_transactions, name="admin_transactions"),
    path("staff/create-admin/", views.create_admin, name="create_admin"),
    path("profile/", views.profile, name="profile"),
    path("staff/delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
]