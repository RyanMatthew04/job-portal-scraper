from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.HomePage,name='home_page'),
    path('signup/',views.SignupPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('home/',views.home,name='home'),
    path('logout/',views.LogoutPage,name='logout'),
    path('save_job', views.save_job, name='save_job'),
    path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
    path('delete_job', views.delete_job, name='delete_job'), 
        
]