from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Web hooks
    path('jobs/notify/', views.jobs_notify, name='jobs_notify'),
    path('jobs/status/<slug:job_id>/', views.jobs_status, name='jobs_status'),
    path('jobs/dl/<slug:job_id>.tar.gz', views.jobs_dl, name='jobs_dl'),

    # User account
    path('user/login/', auth_views.LoginView.as_view(), name='login'),
    path('user/settings/', views.settings, name='settings'),
    path('user/register/', views.register, name="register"),
    path('user/logout/', auth_views.LogoutView.as_view(), name='logout')
]
